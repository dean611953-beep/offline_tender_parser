import os
import streamlit as st
import pandas as pd

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode

from parser.analyzer import analyze_tender
from utils.file_utils import save_uploaded_file, ensure_dir
from exporters.excel_exporter_editable import export_edited_dataframes_to_excel
from utils.text_locator import (
    find_best_paragraph,
    get_context_paragraphs,
    extract_keywords,
    highlight_text_html
)

st.set_page_config(page_title="离线版招标文件拆解工具", layout="wide")
st.title("离线版招标文件拆解工具 V1（稳定修正版）")


OVERVIEW_COLUMNS = [
    "row_id",
    "category",
    "sub_category",
    "text",
    "source_text",
    "page",
    "priority",
    "is_hard_requirement",
    "is_scoring_item",
    "is_risk_item",
    "recommended_chapter"
]

DATE_COLUMNS = [
    "date_type",
    "value",
    "source_text",
    "page"
]

CATEGORY_OPTIONS = ["资格要求", "评分项", "风险项", "材料要求", "格式要求", "其他"]
PRIORITY_OPTIONS = ["高", "中", "低"]


def safe_str(v):
    if v is None:
        return ""
    try:
        if pd.isna(v):
            return ""
    except Exception:
        pass
    return str(v)


def safe_int(v):
    try:
        if v is None or v == "":
            return None
        if pd.isna(v):
            return None
        return int(float(v))
    except Exception:
        return None


def ensure_bool(v):
    if isinstance(v, bool):
        return v
    try:
        if pd.isna(v):
            return False
    except Exception:
        pass
    if v is None:
        return False
    if str(v).lower() in ["true", "1", "yes", "y"]:
        return True
    return False


def ensure_overview_schema(df: pd.DataFrame):
    if df is None or df.empty:
        return pd.DataFrame(columns=OVERVIEW_COLUMNS)

    df = df.copy()
    for col in OVERVIEW_COLUMNS:
        if col not in df.columns:
            df[col] = None

    df = df[OVERVIEW_COLUMNS].copy()

    df["category"] = df["category"].apply(safe_str)
    df["sub_category"] = df["sub_category"].apply(safe_str)
    df["text"] = df["text"].apply(safe_str)
    df["source_text"] = df["source_text"].apply(safe_str)
    df["page"] = df["page"].apply(safe_int)
    df["priority"] = df["priority"].apply(lambda x: safe_str(x) if safe_str(x) in PRIORITY_OPTIONS else "中")
    df["is_hard_requirement"] = df["is_hard_requirement"].apply(ensure_bool)
    df["is_scoring_item"] = df["is_scoring_item"].apply(ensure_bool)
    df["is_risk_item"] = df["is_risk_item"].apply(ensure_bool)
    df["recommended_chapter"] = df["recommended_chapter"].apply(safe_str)

    df["category"] = df["category"].apply(lambda x: x if x in CATEGORY_OPTIONS else "其他")
    return df


def ensure_dates_schema(df: pd.DataFrame):
    if df is None or df.empty:
        return pd.DataFrame(columns=DATE_COLUMNS)

    df = df.copy()
    for col in DATE_COLUMNS:
        if col not in df.columns:
            df[col] = None

    df = df[DATE_COLUMNS].copy()
    df["date_type"] = df["date_type"].apply(safe_str)
    df["value"] = df["value"].apply(safe_str)
    df["source_text"] = df["source_text"].apply(safe_str)
    df["page"] = df["page"].apply(safe_int)
    return df


def ensure_basic_info_schema(df: pd.DataFrame):
    if df is None or df.empty:
        return pd.DataFrame([{
            "project_name": "",
            "tender_no": "",
            "tender_unit": "",
            "budget": ""
        }])

    df = df.copy()
    for col in ["project_name", "tender_no", "tender_unit", "budget"]:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].apply(safe_str)

    return df[["project_name", "tender_no", "tender_unit", "budget"]]


def ensure_chapters_schema(df: pd.DataFrame):
    if df is None or df.empty:
        return pd.DataFrame(columns=["chapter"])

    df = df.copy()
    if "chapter" not in df.columns:
        df["chapter"] = ""
    df["chapter"] = df["chapter"].apply(safe_str)
    return df[["chapter"]]


def deduplicate_requirements_df(df: pd.DataFrame):
    if df is None or df.empty:
        return ensure_overview_schema(df)
    df = ensure_overview_schema(df)
    df = df.drop_duplicates(subset=["category", "text", "page"])
    return df.reset_index(drop=True)


def ensure_row_id(df: pd.DataFrame):
    df = ensure_overview_schema(df).copy()

    if "row_id" not in df.columns:
        df["row_id"] = None

    existing_numeric = []
    for v in df["row_id"]:
        try:
            if v is not None and v != "" and not pd.isna(v):
                existing_numeric.append(int(float(v)))
        except Exception:
            pass

    current_max = max(existing_numeric) if existing_numeric else 0

    new_values = []
    for v in df["row_id"]:
        try:
            if v is not None and v != "" and not pd.isna(v):
                new_values.append(int(float(v)))
            else:
                current_max += 1
                new_values.append(current_max)
        except Exception:
            current_max += 1
            new_values.append(current_max)

    df["row_id"] = new_values
    return df


def requirements_to_df(items):
    if not items:
        return pd.DataFrame(columns=OVERVIEW_COLUMNS[1:])
    rows = [x.model_dump() for x in items]
    return pd.DataFrame(rows)


def result_to_dataframes(result):
    basic_info_df = pd.DataFrame([result.project_info.model_dump()])
    basic_info_df = ensure_basic_info_schema(basic_info_df)

    dates_df = pd.DataFrame([x.model_dump() for x in result.dates]) if result.dates else pd.DataFrame(columns=DATE_COLUMNS)
    dates_df = ensure_dates_schema(dates_df)

    qualifications_df = requirements_to_df(result.qualifications)
    scoring_df = requirements_to_df(result.scoring_items)
    risks_df = requirements_to_df(result.risk_items)
    materials_df = requirements_to_df(result.material_items)
    formats_df = requirements_to_df(result.format_items)

    overview_df = pd.concat(
        [qualifications_df, scoring_df, risks_df, materials_df, formats_df],
        ignore_index=True
    ) if any(not df.empty for df in [qualifications_df, scoring_df, risks_df, materials_df, formats_df]) else pd.DataFrame(columns=OVERVIEW_COLUMNS[1:])

    overview_df = ensure_overview_schema(overview_df)
    overview_df = deduplicate_requirements_df(overview_df)
    overview_df = ensure_row_id(overview_df)

    chapters_df = pd.DataFrame({"chapter": result.chapter_suggestions}) if result.chapter_suggestions else pd.DataFrame(columns=["chapter"])
    chapters_df = ensure_chapters_schema(chapters_df)

    page_texts_df = pd.DataFrame(result.page_texts) if result.page_texts else pd.DataFrame(columns=["page", "text"])
    if not page_texts_df.empty:
        if "page" not in page_texts_df.columns:
            page_texts_df["page"] = None
        if "text" not in page_texts_df.columns:
            page_texts_df["text"] = ""
        page_texts_df["page"] = page_texts_df["page"].apply(safe_int)
        page_texts_df["text"] = page_texts_df["text"].apply(safe_str)

    return {
        "basic_info_df": basic_info_df,
        "dates_df": dates_df,
        "chapters_df": chapters_df,
        "page_texts_df": page_texts_df,
        "overview_df": overview_df
    }


def split_overview_df(overview_df):
    overview_df = ensure_row_id(ensure_overview_schema(overview_df))

    qualifications_df = overview_df[overview_df["category"] == "资格要求"].copy()
    scoring_df = overview_df[overview_df["category"] == "评分项"].copy()
    risks_df = overview_df[overview_df["category"] == "风险项"].copy()
    materials_df = overview_df[overview_df["category"] == "材料要求"].copy()
    formats_df = overview_df[overview_df["category"] == "格式要求"].copy()

    for df in [qualifications_df, scoring_df, risks_df, materials_df, formats_df]:
        df.drop(columns=["row_id"], inplace=True, errors="ignore")

    return qualifications_df, scoring_df, risks_df, materials_df, formats_df


def get_grid_data(grid_response):
    if not grid_response:
        return pd.DataFrame(columns=OVERVIEW_COLUMNS)

    data = None
    if isinstance(grid_response, dict):
        data = grid_response.get("data", None)

    if data is None:
        return pd.DataFrame(columns=OVERVIEW_COLUMNS)

    if isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        df = pd.DataFrame(data)

    return ensure_row_id(ensure_overview_schema(df))


def get_selected_row(grid_response):
    if not grid_response:
        return None

    selected_rows = None
    if isinstance(grid_response, dict):
        selected_rows = grid_response.get("selected_rows", None)

    if selected_rows is None:
        return None

    if isinstance(selected_rows, list) and len(selected_rows) > 0:
        first = selected_rows[0]
        if isinstance(first, dict):
            return first
        if hasattr(first, "to_dict"):
            return first.to_dict()

    if hasattr(selected_rows, "empty") and not selected_rows.empty:
        try:
            return selected_rows.iloc[0].to_dict()
        except Exception:
            pass

    return None


def merge_edited_subset(full_df: pd.DataFrame, edited_subset_df: pd.DataFrame):
    full_df = ensure_row_id(ensure_overview_schema(full_df))
    edited_subset_df = ensure_row_id(ensure_overview_schema(edited_subset_df))

    full_map = {int(row["row_id"]): row.to_dict() for _, row in full_df.iterrows()}
    edited_map = {int(row["row_id"]): row.to_dict() for _, row in edited_subset_df.iterrows()}

    for rid, row_dict in edited_map.items():
        full_map[rid] = row_dict

    merged_rows = list(full_map.values())
    merged_df = pd.DataFrame(merged_rows)
    merged_df = ensure_row_id(ensure_overview_schema(merged_df))
    merged_df = merged_df.sort_values("row_id").reset_index(drop=True)
    return merged_df


def build_aggrid(df: pd.DataFrame, height=420):
    df = ensure_row_id(ensure_overview_schema(df))

    gb = GridOptionsBuilder.from_dataframe(df)

    gb.configure_default_column(
        editable=True,
        groupable=True,
        wrapText=True,
        autoHeight=True,
        resizable=True
    )

    gb.configure_selection(
        selection_mode="single",
        use_checkbox=False
    )

    gb.configure_column("row_id", header_name="ID", width=70, editable=False)
    gb.configure_column(
        "category",
        header_name="分类",
        editable=True,
        cellEditor="agSelectCellEditor",
        cellEditorParams={"values": CATEGORY_OPTIONS},
        width=110
    )
    gb.configure_column("sub_category", header_name="子分类", width=120)
    gb.configure_column("text", header_name="抽取内容", width=240)
    gb.configure_column("source_text", header_name="来源原文", width=340)
    gb.configure_column("page", header_name="页码", width=80)
    gb.configure_column(
        "priority",
        header_name="优先级",
        editable=True,
        cellEditor="agSelectCellEditor",
        cellEditorParams={"values": PRIORITY_OPTIONS},
        width=90
    )
    gb.configure_column("recommended_chapter", header_name="建议章节", width=180)
    gb.configure_column("is_hard_requirement", header_name="硬性要求", width=100)
    gb.configure_column("is_scoring_item", header_name="评分项", width=90)
    gb.configure_column("is_risk_item", header_name="风险项", width=90)

    grid_options = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        height=height,
        width="100%",
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_mode=GridUpdateMode.MODEL_CHANGED | GridUpdateMode.SELECTION_CHANGED,
        fit_columns_on_grid_load=False,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=False
    )

    return grid_response


if "parsed_data" not in st.session_state:
    st.session_state["parsed_data"] = None

if "edited_data" not in st.session_state:
    st.session_state["edited_data"] = None


uploaded_file = st.file_uploader("上传招标文件（PDF / DOCX）", type=["pdf", "docx"])

col_a, col_b = st.columns([1, 1])

with col_a:
    if st.button("开始解析", use_container_width=True):
        if uploaded_file is None:
            st.warning("请先上传文件")
        else:
            with st.spinner("正在解析文件，请稍候..."):
                file_path = save_uploaded_file(uploaded_file)
                result = analyze_tender(file_path)
                parsed_data = result_to_dataframes(result)
                st.session_state["parsed_data"] = parsed_data
                st.session_state["edited_data"] = parsed_data
            st.success("解析完成")

with col_b:
    if st.button("清空结果", use_container_width=True):
        st.session_state["parsed_data"] = None
        st.session_state["edited_data"] = None
        st.rerun()


if st.session_state["edited_data"] is not None:
    data = st.session_state["edited_data"]

    basic_info_df = ensure_basic_info_schema(data.get("basic_info_df"))
    dates_df = ensure_dates_schema(data.get("dates_df"))
    chapters_df = ensure_chapters_schema(data.get("chapters_df"))
    page_texts_df = data.get("page_texts_df", pd.DataFrame(columns=["page", "text"]))
    overview_full_df = ensure_row_id(ensure_overview_schema(data.get("overview_df")))

    st.markdown("---")
    st.header("一、项目基本信息")
    basic_info_df = st.data_editor(
        basic_info_df,
        num_rows="dynamic",
        use_container_width=True,
        key="basic_info_editor"
    )
    basic_info_df = ensure_basic_info_schema(basic_info_df)

    st.header("二、时间节点")
    dates_df = st.data_editor(
        dates_df,
        num_rows="dynamic",
        use_container_width=True,
        key="dates_editor"
    )
    dates_df = ensure_dates_schema(dates_df)

    st.markdown("---")
    st.header("三、总览汇总表（点击行查看定位结果）")

    overview_category = st.selectbox(
        "按分类筛选",
        options=["全部", "资格要求", "评分项", "风险项", "材料要求", "格式要求"]
    )

    if overview_category != "全部":
        display_df = overview_full_df[overview_full_df["category"] == overview_category].copy()
    else:
        display_df = overview_full_df.copy()

    display_df = ensure_row_id(ensure_overview_schema(display_df))

    grid_response = build_aggrid(display_df, height=420)
    edited_display_df = get_grid_data(grid_response)

    if overview_category != "全部":
        merged_overview_df = merge_edited_subset(overview_full_df, edited_display_df)
    else:
        merged_overview_df = ensure_row_id(edited_display_df)

    selected_row = get_selected_row(grid_response)

    st.markdown("---")
    st.header("四、定位结果（段落级）")

    if selected_row:
        selected_page = safe_int(selected_row.get("page", None))
        selected_text = safe_str(selected_row.get("text", ""))
        selected_source_text = safe_str(selected_row.get("source_text", ""))
        keywords = extract_keywords(selected_source_text, selected_text)

        left, right = st.columns([1, 1])

        with left:
            st.subheader("当前选中记录")
            st.write(f"**ID：** {safe_str(selected_row.get('row_id', ''))}")
            st.write(f"**分类：** {safe_str(selected_row.get('category', ''))}")
            st.write(f"**子分类：** {safe_str(selected_row.get('sub_category', ''))}")
            st.write(f"**页码：** {safe_str(selected_page)}")
            st.write(f"**优先级：** {safe_str(selected_row.get('priority', ''))}")
            st.write(f"**建议章节：** {safe_str(selected_row.get('recommended_chapter', ''))}")

            st.markdown("**抽取内容（高亮）**", unsafe_allow_html=True)
            st.markdown(
                f"<div style='padding:8px;border:1px solid #ddd;border-radius:6px;'>{highlight_text_html(selected_text, keywords)}</div>",
                unsafe_allow_html=True
            )

            st.markdown("**来源原文（高亮）**", unsafe_allow_html=True)
            st.markdown(
                f"<div style='padding:8px;border:1px solid #ddd;border-radius:6px;max-height:220px;overflow:auto;'>{highlight_text_html(selected_source_text, keywords)}</div>",
                unsafe_allow_html=True
            )

        with right:
            st.subheader("段落定位")

            if selected_page is not None and not page_texts_df.empty:
                matched = page_texts_df[page_texts_df["page"] == selected_page]
                if not matched.empty:
                    page_text = safe_str(matched.iloc[0]["text"])

                    best_paragraph, best_idx, paragraphs = find_best_paragraph(
                        page_text=page_text,
                        source_text=selected_source_text,
                        target_text=selected_text
                    )

                    if best_paragraph:
                        st.markdown("**命中段落（高亮）**", unsafe_allow_html=True)
                        st.markdown(
                            f"<div style='padding:10px;border:2px solid #faad14;border-radius:6px;background:#fffbe6;'>{highlight_text_html(best_paragraph, keywords)}</div>",
                            unsafe_allow_html=True
                        )

                        context = get_context_paragraphs(paragraphs, best_idx, window=2)
                        st.markdown("**上下文段落**", unsafe_allow_html=True)
                        for item in context:
                            border = "2px solid #faad14" if item["is_hit"] else "1px solid #ddd"
                            bg = "#fffbe6" if item["is_hit"] else "#fafafa"
                            st.markdown(
                                f"""
                                <div style='margin-bottom:8px;padding:8px;border:{border};border-radius:6px;background:{bg};'>
                                    <div style='font-size:12px;color:#888;'>段落序号：{item["index"] + 1}</div>
                                    <div>{highlight_text_html(item["text"], keywords)}</div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                    else:
                        st.warning("未定位到明确段落，仅展示整页原文。")

                    st.markdown("**整页原文（高亮）**", unsafe_allow_html=True)
                    page_html = highlight_text_html(page_text, keywords)
                    st.markdown(
                        f"<div style='padding:10px;border:1px solid #ddd;border-radius:6px;max-height:420px;overflow:auto;white-space:pre-wrap;'>{page_html}</div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.warning("未找到对应页原文")
            else:
                st.info("当前记录没有页码信息")

        st.subheader("同页其他抽取结果")
        if selected_page is not None:
            same_page_df = merged_overview_df[merged_overview_df["page"] == selected_page].copy()
            if not same_page_df.empty:
                st.dataframe(same_page_df, use_container_width=True, height=180)
            else:
                st.info("该页暂无其他抽取结果")

        if keywords:
            st.caption("关键词高亮：" + " / ".join(keywords))

    else:
        st.info("请在上方总览汇总表中点击/选中一行，系统会自动展示段落定位与高亮结果。")

    st.markdown("---")
    st.header("五、标书框架建议")
    chapters_df = st.data_editor(
        chapters_df,
        num_rows="dynamic",
        use_container_width=True,
        key="chapters_editor"
    )
    chapters_df = ensure_chapters_schema(chapters_df)

    st.session_state["edited_data"] = {
        "basic_info_df": basic_info_df,
        "dates_df": dates_df,
        "chapters_df": chapters_df,
        "page_texts_df": page_texts_df,
        "overview_df": merged_overview_df
    }

    st.markdown("---")
    st.header("六、导出结果")

    qualifications_df, scoring_df, risks_df, materials_df, formats_df = split_overview_df(merged_overview_df)

    if st.button("保存修正结果到 Excel", use_container_width=True):
        ensure_dir("data/outputs")
        output_path = os.path.join("data/outputs", "招标拆解结果_人工修正.xlsx")

        export_edited_dataframes_to_excel(
            basic_info_df=basic_info_df,
            dates_df=dates_df,
            qualifications_df=qualifications_df,
            scoring_df=scoring_df,
            risks_df=risks_df,
            materials_df=materials_df,
            formats_df=formats_df,
            chapters_df=chapters_df,
            output_path=output_path
        )
        st.success(f"已保存到：{output_path}")

    output_path = os.path.join("data/outputs", "招标拆解结果_人工修正.xlsx")
    if os.path.exists(output_path):
        with open(output_path, "rb") as f:
            st.download_button(
                label="下载修正后的 Excel",
                data=f,
                file_name="招标拆解结果_人工修正.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
