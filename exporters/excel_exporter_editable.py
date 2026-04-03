import pandas as pd


def export_edited_dataframes_to_excel(
    basic_info_df,
    dates_df,
    qualifications_df,
    scoring_df,
    risks_df,
    materials_df,
    formats_df,
    chapters_df,
    output_path: str
):
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        if basic_info_df is not None and not basic_info_df.empty:
            basic_info_df.to_excel(writer, sheet_name="项目基本信息", index=False)

        if dates_df is not None and not dates_df.empty:
            dates_df.to_excel(writer, sheet_name="时间节点", index=False)

        if qualifications_df is not None and not qualifications_df.empty:
            qualifications_df.to_excel(writer, sheet_name="资格要求", index=False)

        if scoring_df is not None and not scoring_df.empty:
            scoring_df.to_excel(writer, sheet_name="评分项", index=False)

        if risks_df is not None and not risks_df.empty:
            risks_df.to_excel(writer, sheet_name="风险项", index=False)

        if materials_df is not None and not materials_df.empty:
            materials_df.to_excel(writer, sheet_name="材料要求", index=False)

        if formats_df is not None and not formats_df.empty:
            formats_df.to_excel(writer, sheet_name="格式要求", index=False)

        if chapters_df is not None and not chapters_df.empty:
            chapters_df.to_excel(writer, sheet_name="标书框架建议", index=False)
