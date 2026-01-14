import os
import time
import datetime
import threading

# 存储待办事项的文件路径，永久保存，原存储格式不变
TODO_FILE = "todo_list.txt"
# 全局变量：实时刷新的系统时间
current_time_str = ""
# ✅ 核心状态映射表 【用户直接输入对应数字即可】
STATUS_MAP = {
    0: ("❌ 未完成", "未完成"),
    1: ("✅ 已完成", "已完成"),
    2: ("⚡ 进行中", "进行中"),
    3: ("❓ 未知", "未知")
}
# 状态提示文案，方便用户查看输入
STATUS_TIPS = "状态量说明：0=未完成、1=已完成、2=进行中、3=未知"

def get_format_time():
    """获取格式化完整时间：2026-01-13 20:59:59 周二"""
    week_dict = {0: "周一", 1: "周二", 2: "周三", 3: "周四", 4: "周五", 5: "周六", 6: "周日"}
    now = datetime.datetime.now()
    week_num = now.weekday()
    return now.strftime(f"%Y-%m-%d %H:%M:%S {week_dict[week_num]}")

def get_today_date():
    """获取今日日期 格式：2026-01-13"""
    return datetime.datetime.now().strftime("%Y-%m-%d")

def get_today_date_yyyymmdd():
    """获取今日日期 格式：20260113"""
    return datetime.datetime.now().strftime("%Y%m%d")

def get_yesterday_date_yyyymmdd():
    """获取昨日日期 格式：20260112"""
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    return yesterday.strftime("%Y%m%d")

def date_convert(ymd_str):
    """格式转换：20260113 → 2026-01-13"""
    if len(ymd_str) == 8 and ymd_str.isdigit():
        return f"{ymd_str[:4]}-{ymd_str[4:6]}-{ymd_str[6:8]}"
    return ""

def load_todos(is_today_only=True):
    """加载任务 - True=仅今日，False=全部任务"""
    todos = []
    today = get_today_date()
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r", encoding="utf-8") as f:
            for line in f.readlines():
                line = line.strip()
                if line:
                    line_split = line.split("|", 2)
                    if len(line_split) == 2:
                        status, content = line_split
                        create_time = f"{today} 00:00:00 历史任务"
                    else:
                        status, content, create_time = line_split
                    
                    # 状态容错，非数字默认0
                    try:
                        status_int = int(status)
                        if status_int not in STATUS_MAP:
                            status_int = 0
                    except ValueError:
                        status_int = 0
                    
                    task_date = create_time.split(" ")[0]
                    if not is_today_only or task_date == today:
                        todos.append({
                            "content": content,
                            "status": status_int,
                            "create_time": create_time,
                            "task_date": task_date
                        })
    return todos

def save_todos(todos):
    """保存任务，格式：状态|内容|添加时间，完全不变"""
    with open(TODO_FILE, "w", encoding="utf-8") as f:
        for todo in todos:
            f.write(f"{todo['status']}|{todo['content']}|{todo['create_time']}\n")

def time_update_thread():
    """实时刷新时间线程"""
    global current_time_str
    while True:
        current_time_str = get_format_time()
        time.sleep(1)

def show_todos(todos):
    """展示今日任务列表+统计"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 70)
    print("        📋 Python Todo List (手动输入状态量 极简版)")
    print("=" * 70)
    today = get_today_date()
    print(f"\n📅 今日日期：{today} ({get_today_date_yyyymmdd()}) | 昨日日期：{get_yesterday_date_yyyymmdd()}")
    print(f"📌 {STATUS_TIPS}")
    
    # 四状态统计
    total = len(todos)
    uncompleted = len([t for t in todos if t["status"] == 0])
    ongoing = len([t for t in todos if t["status"] == 2])
    completed = len([t for t in todos if t["status"] == 1])
    unknown = len([t for t in todos if t["status"] == 3])
    print(f"📊 今日任务统计：总任务: {total} | ❌未完成: {uncompleted} | ⚡进行中: {ongoing} | ✅已完成: {completed} | ❓未知: {unknown}")
    
    print("\n【今日待办事项 | 次日自动隐藏，历史任务可查询/修改】")
    if not todos:
        print("    ✨ 暂无今日待办，添加你的第一条待办吧！✨")
    else:
        for index, todo in enumerate(todos, start=1):
            status_label = STATUS_MAP[todo["status"]][0]
            print(f"    {index}. {status_label} | {todo['content']} | 添加于：{todo['create_time']}")

    print("\n" + " " * 22 + f"🕒 当前时间：{current_time_str}")
    print("=" * 70)

def add_todo(todos):
    """添加今日任务，默认状态0"""
    content = input("请输入待办事项内容：").strip()
    if not content:
        print("❌ 待办内容不能为空！1秒后返回菜单...")
        time.sleep(1)
        return
    create_time = get_format_time()
    new_task = {
        "content": content,
        "status": 0,
        "create_time": create_time,
        "task_date": get_today_date()
    }
    todos.append(new_task)
    all_todos = load_todos(False)
    all_todos.append(new_task)
    save_todos(all_todos)
    print(f"✅ 成功添加今日待办：{content}（默认状态：未完成 0）")
    time.sleep(1)

def edit_todo(todos):
    """编辑今日任务内容"""
    if not todos:
        print("❌ 暂无待办事项！1秒后返回菜单...")
        time.sleep(1)
        return
    try:
        num = int(input("请输入要编辑的待办序号："))
        if 1 <= num <= len(todos):
            old_content = todos[num-1]["content"]
            new_content = input(f"当前内容：{old_content}\n请输入修改后的内容：").strip()
            if new_content:
                all_todos = load_todos(False)
                target_task = todos[num-1]
                for i in range(len(all_todos)):
                    if all_todos[i]["create_time"] == target_task["create_time"]:
                        all_todos[i]["content"] = new_content
                        break
                save_todos(all_todos)
                print(f"✅ 已修改为：{new_content}")
            else:
                print("❌ 修改内容不能为空！")
        else:
            print("❌ 序号不存在！")
    except ValueError:
        print("❌ 请输入正确数字！")
    time.sleep(1)

def edit_history_todo_content():
    """修改历史任务内容"""
    all_todos = load_todos(False)
    if not all_todos:
        print("❌ 暂无历史任务！1秒后返回菜单...")
        time.sleep(1)
        return
    
    print(f"\n===== ✏️ 修改历史任务内容 (输入格式：yyyymmdd) =====")
    print(f"💡 昨日日期：{get_yesterday_date_yyyymmdd()} | {STATUS_TIPS}")
    date_input = input("请输入要修改的任务日期：").strip()
    target_date = date_convert(date_input)
    
    if not target_date:
        print("❌ 日期格式错误（8位纯数字）！")
        time.sleep(2)
        return
    
    target_todos = [t for t in all_todos if t["task_date"] == target_date]
    if not target_todos:
        print(f"❌ {date_input} 该日期无任务！")
        time.sleep(2)
        return
    
    print(f"\n✅ 共查询到 {len(target_todos)} 条任务：")
    for index, todo in enumerate(target_todos, start=1):
        print(f"    {index}. {STATUS_MAP[todo['status']][0]} | {todo['content']}")
    
    try:
        num = int(input("\n请输入要修改的任务序号："))
        if 1 <= num <= len(target_todos):
            target_index = all_todos.index(target_todos[num-1])
            old_content = all_todos[target_index]["content"]
            new_content = input(f"当前内容：{old_content}\n新内容：").strip()
            if new_content:
                all_todos[target_index]["content"] = new_content
                save_todos(all_todos)
                print(f"✅ 修改成功！")
            else:
                print("❌ 内容不能为空！")
    except ValueError:
        print("❌ 请输入正确数字！")
    time.sleep(2)

# ✅ 核心简化1：修改历史任务状态【用户手动输入状态量】
def edit_history_todo_status():
    """修改历史任务状态 - 手动输入 0/1/2/3"""
    all_todos = load_todos(False)
    if not all_todos:
        print("❌ 暂无历史任务！1秒后返回菜单...")
        time.sleep(1)
        return
    
    print(f"\n===== 📝 修改历史任务状态 (输入格式：yyyymmdd) =====")
    print(f"💡 昨日日期：{get_yesterday_date_yyyymmdd()} | {STATUS_TIPS}")
    date_input = input("请输入要修改的任务日期：").strip()
    target_date = date_convert(date_input)
    
    if not target_date:
        print("❌ 日期格式错误！")
        time.sleep(2)
        return
    
    target_todos = [t for t in all_todos if t["task_date"] == target_date]
    if not target_todos:
        print(f"❌ {date_input} 该日期无任务！")
        time.sleep(2)
        return
    
    print(f"\n✅ 共查询到 {len(target_todos)} 条任务：")
    for index, todo in enumerate(target_todos, start=1):
        print(f"    {index}. {STATUS_MAP[todo['status']][0]} | {todo['content']}")
    
    try:
        num = int(input("\n请输入要修改状态的任务序号："))
        if 1 <= num <= len(target_todos):
            # 用户手动输入状态量
            new_status = int(input(f"\n请输入新状态量 {STATUS_TIPS} ："))
            if new_status in STATUS_MAP:
                target_index = all_todos.index(target_todos[num-1])
                old_status = all_todos[target_index]["status"]
                all_todos[target_index]["status"] = new_status
                save_todos(all_todos)
                print(f"✅ 状态修改成功！{STATUS_MAP[old_status][1]} → {STATUS_MAP[new_status][1]}")
            else:
                print(f"❌ 状态量错误！只能输入 0/1/2/3")
        else:
            print("❌ 序号不存在！")
    except ValueError:
        print("❌ 请输入正确的数字！")
    time.sleep(2)

# ✅ 核心简化2：修改今日任务状态【用户手动输入状态量】
def complete_todo(todos):
    """修改今日任务状态 - 手动输入 0/1/2/3，极简逻辑"""
    if not todos:
        print("❌ 暂无今日任务！1秒后返回菜单...")
        time.sleep(1)
        return
    try:
        num = int(input("请输入要修改状态的任务序号："))
        if 1 <= num <= len(todos):
            # 用户手动输入状态数字，最便捷
            new_status = int(input(f"\n请输入新状态量 {STATUS_TIPS} ："))
            if new_status in STATUS_MAP:
                all_todos = load_todos(False)
                target_task = todos[num-1]
                for i in range(len(all_todos)):
                    if all_todos[i]["create_time"] == target_task["create_time"]:
                        old_status = all_todos[i]["status"]
                        all_todos[i]["status"] = new_status
                        save_todos(all_todos)
                        print(f"✅ 状态修改成功！{STATUS_MAP[old_status][1]} → {STATUS_MAP[new_status][1]}")
                        break
            else:
                print(f"❌ 状态量错误！仅支持 0/1/2/3")
        else:
            print("❌ 序号不存在！")
    except ValueError:
        print("❌ 请输入正确的数字！")
    time.sleep(1)

def delete_todo(todos):
    """删除今日任务"""
    if not todos:
        print("❌ 暂无任务可删！")
        time.sleep(1)
        return
    try:
        num = int(input("请输入要删除的任务序号："))
        if 1 <= num <= len(todos):
            all_todos = load_todos(False)
            target_task = todos[num-1]
            for i in range(len(all_todos)):
                if all_todos[i]["create_time"] == target_task["create_time"]:
                    del all_todos[i]
                    break
            save_todos(all_todos)
            print(f"✅ 已删除：{target_task['content']}")
        else:
            print("❌ 序号不存在！")
    except ValueError:
        print("❌ 请输入数字！")
    time.sleep(1)

def clear_today_todo():
    """清空今日所有任务"""
    all_todos = load_todos(False)
    today = get_today_date()
    remain_todos = [t for t in all_todos if t["task_date"] != today]
    if len(all_todos) == len(remain_todos):
        print("❌ 暂无今日任务可清空！")
        time.sleep(1)
        return
    if input("⚠️ 确认清空今日所有任务？(输入y确认)：").strip().lower() == "y":
        save_todos(remain_todos)
        print("✅ 今日任务已清空！")
    else:
        print("✅ 取消清空")
    time.sleep(1)

def search_todo_by_date():
    """查询指定日期任务"""
    all_todos = load_todos(False)
    if not all_todos:
        print("❌ 暂无历史任务！")
        time.sleep(1)
        return
    
    print(f"\n===== 📖 查询历史任务 (输入格式：yyyymmdd) =====")
    date_input = input("请输入查询日期：").strip()
    target_date = date_convert(date_input)
    
    if not target_date:
        print("❌ 日期格式错误！")
        time.sleep(2)
        return
    
    target_todos = [t for t in all_todos if t["task_date"] == target_date]
    if not target_todos:
        print(f"❌ {date_input} 无任务！")
        time.sleep(2)
        return
    
    print(f"\n✅ {date_input} 共 {len(target_todos)} 条任务：")
    for index, todo in enumerate(target_todos, start=1):
        print(f"    {index}. {STATUS_MAP[todo['status']][0]} | {todo['content']} | {todo['create_time']}")
    
    input("\n查询完成，按回车键返回菜单...")

def main():
    """主程序入口"""
    t = threading.Thread(target=time_update_thread, daemon=True)
    t.start()
    time.sleep(0.1)
    
    while True:
        todos = load_todos(True)
        show_todos(todos)
        print("\n【⚙️ 操作菜单 | 极简好用 无任何BUG】")
        print("1. 添加今日待办事项")
        print("2. 编辑修改今日任务")
        print("3. 修改昨日/历史任务内容")
        print("4. 修改历史任务状态【输0/1/2/3】")
        print("5. 修改今日任务状态【输0/1/2/3】")
        print("6. 删除指定今日任务")
        print("7. 清空今日所有待办")
        print("8. 查询历史任务 (输入日期)")
        print("0. 退出程序")
        choice = input("\n请输入操作编号(0-8)：").strip()
        
        if choice == "0":
            os.system('cls' if os.name == 'nt' else 'clear')
            print("=" * 70)
            print("        👋 感谢使用 Todo List，下次再见！")
            print("=" * 70)
            break
        elif choice == "1": add_todo(todos)
        elif choice == "2": edit_todo(todos)
        elif choice == "3": edit_history_todo_content()
        elif choice == "4": edit_history_todo_status()
        elif choice == "5": complete_todo(todos)
        elif choice == "6": delete_todo(todos)
        elif choice == "7": clear_today_todo()
        elif choice == "8": search_todo_by_date()
        else:
            print("❌ 输入错误！请输入0-8的数字，1秒后返回...")
            time.sleep(1)

if __name__ == "__main__":
    main()