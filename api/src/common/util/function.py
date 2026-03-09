from datetime import datetime

def group_conversations_by_time(conv_list, reference_time: datetime):
    """
    根据更新时间与参考时间的关系分组对话

    Args:
        conversations_dict: 对话字典
        reference_time: 参考时间(datetime对象)

    Returns:
        分组后的字典
    """
    # 初始化分组
    today = []
    yesterday = []
    last7days = []
    older = []

    for conv in conv_list:

        created_at_str = conv.get("created_at", "")
        if not created_at_str:
            continue

        # 将字符串转换为datetime对象
        created_at = datetime.fromisoformat(created_at_str)

        # 计算时间差（天）
        time_diff = reference_time.date() - created_at.date()
        days_diff = time_diff.days

        id = conv["conv_id"]

        print(f"对话{id}的时间差是{days_diff}")

        # 根据时间差分组
        if days_diff == 0:
            # 今天（同一天）
            today.append(
                {
                    "conv_id": conv["conv_id"],
                    "title": conv["title"],
                    "created_at": created_at_str,
                }
            )
        elif days_diff == 1:
            # 昨天
            yesterday.append(
                {
                    "conv_id": conv["conv_id"],
                    "title": conv["title"],
                    "created_at": created_at_str,
                }
            )
        elif 2 <= days_diff <= 6:
            # 过去7天内（不包括今天和昨天）
            last7days.append(
                {
                    "conv_id": conv["conv_id"],
                    "title": conv["title"],
                    "created_at": created_at_str,
                }
            )
        elif days_diff >= 7:
            # 更早的
            older.append(
                {
                    "conv_id": conv["conv_id"],
                    "title": conv["title"],
                    "created_at": created_at_str,
                }
            )

    # 按更新时间降序排序每个组
    for group in [today, yesterday, last7days, older]:
        group.sort(key=lambda x: x["created_at"], reverse=True)

    return {
        "today": today,
        "yesterday": yesterday,
        "last7days": last7days,
        "older": older,
    }