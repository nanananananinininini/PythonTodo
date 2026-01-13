import os
import time
import datetime
import threading

# 存储待办事项的文件路径，永久保存，完全不修改原存储格式
TODO_FILE = "todo_list.txt"
# 全局变量：实时刷新的系统时间
current_time_str = ""

def get_format_time():
    """获取格式化完整时间：2026-01-13 20:59:59 周二"""
    week_dict = {0: "周一", 1: "周二", 2: "周三", 3: "周四", 4: "周五", 5: "周六", 6: "周日"}
    now = datetime.datetime.now()
    week_num = now.weekday()
    return now.strftime(f"%Y-%m-%d %H:%M:%S {week_dict[week_num]}")

def get_today_date():
    """获取今日日期 格式：2026-01-13，用于分日展示"""
    return datetime.datetime.now().strftime("%Y-%m-%d")

def get_today_date_yyyymmdd():
    """获取今日日期 格式：20260113，用于日期匹配"""
    return datetime.datetime.now().strftime("%Y%m%d")

def get_yesterday_date_yyyymmdd():
    """获取昨日日期 格式：20260112，快捷定位昨日任务"""
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    return yesterday.strftime("%Y%m%d")

def date_convert(ymd_str):
    """格式转换：20260113 → 2026-01-13，用于查询/修改匹配"""
    if len(ymd_str) == 8 and ymd_str.isdigit():
        return f"{ymd_str[:4]}-{ymd_str[4:6]}-{ymd_str[6:8]}"
    return ""

def load_todos(is_today_only=True):
    """
    加载任务核心方法 - 完全不修改文件解析逻辑，兼容所有历史格式
    is_today_only=True → 只加载今日任务（默认，分日展示核心）
    is_today_only=False → 加载全部任务（供查询/修改功能使用）
    """
    todos = []
    today = get_today_date()
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r", encoding="utf-8") as f:
            for line in f.readlines():
                line = line.strip()
                if line:
                    line_split = line.split("|", 2)
                    # 兼容旧2字段/新3字段，完全不变的解析逻辑，杜绝报错
                    if len(line_split) == 2:
                        status, content = line_split
                        create_time = "历史任务(无添加时间)"
                    else:
                        status, content, create_time = line_split
                    
                    # 核心：分日加载逻辑
                    task_date = create_time.split(" ")[0]  # 提取任务的创建日期
                    if not is_today_only or task_date == today:
                        todos.append({
                            "content": content,
                            "completed": status == "1",
                            "create_time": create_time,
                            "task_date": task_date
                        })
    return todos

def save_todos(todos):
    """保存任务 - 完全不修改原文件存储格式 状态|内容|添加时间，完美兼容"""
    with open(TODO_FILE, "w", encoding="utf-8") as f:
        for todo in todos:
            status = "1" if todo["completed"] else "0"
            f.write(f"{status}|{todo['content']}|{todo['create_time']}\n")

def time_update_thread():
    """独立线程：每秒刷新实时时间，秒数自动跳动不卡顿"""
    global current_time_str
    while True:
        current_time_str = get_format_time()
        time.sleep(1)

def show_todos(todos):
    """展示今日待办 + 实时时间 + 数量统计，界面整洁"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 65)
    print("        📋 Python Todo List (分日展示+历史任务管理完整版)")
    print("=" * 65)
    today = get_today_date()
    today_yyyymmdd = get_today_date_yyyymmdd()
    yesterday_yyyymmdd = get_yesterday_date_yyyymmdd()
    
    # 任务数量统计
    total = len(todos)
    completed = len([t for t in todos if t["completed"]])
    uncompleted = total - completed
    print(f"\n📅 今日日期：{today} ({today_yyyymmdd}) | 昨日日期：{yesterday_yyyymmdd}")
    print(f"📊 今日任务统计：总任务: {total} | ✅已完成: {completed} | ❌未完成: {uncompleted}")
    
    print("\n【今日待办事项 | 次日自动隐藏，历史任务可查询/修改】")
    if not todos:
        print("    ✨ 暂无今日待办，添加你的第一条待办吧！✨")
    else:
        for index, todo in enumerate(todos, start=1):
            status = "✅ 已完成" if todo["completed"] else "❌ 未完成"
            content = todo["content"]
            create_time = todo["create_time"]
            print(f"    {index}. {status} | {content} | 添加于：{create_time}")

    # 右下角实时跳动时间
    print("\n" + " " * 22 + f"🕒 当前时间：{current_time_str}")
    print("=" * 65)

def add_todo(todos):
    """添加今日新任务，格式不变"""
    content = input("请输入待办事项内容：").strip()
    if not content:
        print("❌ 待办内容不能为空！1秒后返回菜单...")
        time.sleep(1)
        return
    create_time = get_format_time()
    todos.append({
        "content": content,
        "completed": False,
        "create_time": create_time,
        "task_date": get_today_date()
    })
    # 修复点：保存全部任务，确保新增任务同步到文件
    save_todos(load_todos(False))
    print(f"✅ 成功添加今日待办：{content}")
    time.sleep(1)

def edit_todo(todos):
    """编辑今日任务内容 - 修复：同步更新总任务列表"""
    if not todos:
        print("❌ 暂无待办事项，无需编辑！1秒后返回菜单...")
        time.sleep(1)
        return
    try:
        num = int(input("请输入要编辑的待办序号："))
        if 1 <= num <= len(todos):
            old_content = todos[num-1]["content"]
            new_content = input(f"当前内容：{old_content}\n请输入修改后的内容：").strip()
            if new_content:
                # 步骤1：获取全部任务列表
                all_todos = load_todos(False)
                # 步骤2：找到今日任务在总列表中的位置并修改
                for i in range(len(all_todos)):
                    if all_todos[i]["create_time"] == todos[num-1]["create_time"] and all_todos[i]["content"] == old_content:
                        all_todos[i]["content"] = new_content
                        break
                # 步骤3：保存修改后的总列表
                save_todos(all_todos)
                print(f"✅ 已修改为：{new_content}")
            else:
                print("❌ 修改内容不能为空，编辑取消！")
        else:
            print("❌ 输入的序号不存在！")
    except ValueError:
        print("❌ 请输入正确的数字序号！")
    time.sleep(1)

def edit_history_todo_content():
    """修改指定日期(如昨日)的任务内容，输入yyyymmdd格式日期+序号，不改文件格式"""
    all_todos = load_todos(False)
    if not all_todos:
        print("❌ 暂无任何历史任务可修改！1秒后返回菜单...")
        time.sleep(1)
        return
    
    print("\n===== ✏️  修改历史任务内容 (输入格式：yyyymmdd 如20260113) =====")
    print(f"💡 快捷提示：昨日日期是 {get_yesterday_date_yyyymmdd()}")
    date_input = input("请输入要修改任务的日期(纯数字yyyymmdd)：").strip()
    target_date = date_convert(date_input)
    
    if not target_date:
        print("❌ 日期格式错误！请输入8位纯数字，例如：20260113")
        time.sleep(2)
        return
    
    # 筛选指定日期的所有任务
    target_todos = [t for t in all_todos if t["task_date"] == target_date]
    if not target_todos:
        print(f"❌ {date_input}({target_date}) 该日期暂无任何任务！")
        time.sleep(2)
        return
    
    # 展示该日期的所有任务+序号
    print(f"\n✅ 共查询到 {date_input}({target_date}) 的任务 {len(target_todos)} 条：")
    for index, todo in enumerate(target_todos, start=1):
        status = "✅ 已完成" if todo["completed"] else "❌ 未完成"
        content = todo["content"]
        create_time = todo["create_time"]
        print(f"    任务序号 {index}. {status} | {content} | 添加于：{create_time}")
    
    # 输入序号修改指定任务内容
    try:
        num = int(input("\n请输入要修改的任务序号："))
        if 1 <= num <= len(target_todos):
            # 定位要修改的任务在总列表中的索引
            target_index = all_todos.index(target_todos[num-1])
            old_content = all_todos[target_index]["content"]
            new_content = input(f"当前内容：{old_content}\n请输入修改后的内容：").strip()
            if new_content:
                all_todos[target_index]["content"] = new_content
                save_todos(all_todos)
                print(f"✅ 已成功修改任务内容为：{new_content}")
            else:
                print("❌ 修改内容不能为空，操作取消！")
        else:
            print("❌ 输入的任务序号不存在！")
    except ValueError:
        print("❌ 请输入正确的数字序号！")
    
    time.sleep(2)

def edit_history_todo_status():
    """修改指定日期任务的完成状态，输入yyyymmdd格式日期+序号，双向切换状态"""
    all_todos = load_todos(False)
    if not all_todos:
        print("❌ 暂无任何历史任务可修改状态！1秒后返回菜单...")
        time.sleep(1)
        return
    
    print("\n===== 📝 修改历史任务状态 (输入格式：yyyymmdd 如20260113) =====")
    print(f"💡 快捷提示：昨日日期是 {get_yesterday_date_yyyymmdd()}")
    date_input = input("请输入要修改状态的任务日期(纯数字yyyymmdd)：").strip()
    target_date = date_convert(date_input)
    
    if not target_date:
        print("❌ 日期格式错误！请输入8位纯数字，例如：20260113")
        time.sleep(2)
        return
    
    # 筛选指定日期的所有任务
    target_todos = [t for t in all_todos if t["task_date"] == target_date]
    if not target_todos:
        print(f"❌ {date_input}({target_date}) 该日期暂无任何任务！")
        time.sleep(2)
        return
    
    # 展示该日期的所有任务+序号+当前状态
    print(f"\n✅ 共查询到 {date_input}({target_date}) 的任务 {len(target_todos)} 条：")
    for index, todo in enumerate(target_todos, start=1):
        status = "✅ 已完成" if todo["completed"] else "❌ 未完成"
        content = todo["content"]
        create_time = todo["create_time"]
        print(f"    任务序号 {index}. {status} | {content} | 添加于：{create_time}")
    
    # 输入序号修改指定任务状态
    try:
        num = int(input("\n请输入要修改状态的任务序号："))
        if 1 <= num <= len(target_todos):
            # 定位要修改的任务在总列表中的索引
            target_index = all_todos.index(target_todos[num-1])
            old_status = all_todos[target_index]["completed"]
            # 状态双向切换：已完成 ↔ 未完成
            all_todos[target_index]["completed"] = not old_status
            new_status = "✅ 已完成" if all_todos[target_index]["completed"] else "❌ 未完成"
            
            save_todos(all_todos)
            print(f"✅ 任务状态修改成功！从 {'已完成' if old_status else '未完成'} → {new_status[2:]}")
        else:
            print("❌ 输入的任务序号不存在！")
    except ValueError:
        print("❌ 请输入正确的数字序号！")
    
    time.sleep(2)

def complete_todo(todos):
    """标记今日任务完成/未完成 - 修复：基于总任务列表修改，确保同步"""
    if not todos:
        print("❌ 暂无待办事项，无需标记完成！1秒后返回菜单...")
        time.sleep(1)
        return
    try:
        num = int(input("请输入要标记的待办序号："))
        if 1 <= num <= len(todos):
            # 修复核心逻辑：
            # 1. 获取全部任务
            all_todos = load_todos(False)
            # 2. 匹配今日任务在总列表中的位置
            target_task = todos[num-1]
            for i in range(len(all_todos)):
                if all_todos[i]["create_time"] == target_task["create_time"] and all_todos[i]["content"] == target_task["content"]:
                    # 3. 修改总任务的状态
                    all_todos[i]["completed"] = not all_todos[i]["completed"]
                    break
            # 4. 保存总任务
            save_todos(all_todos)
            status = "已完成" if not target_task["completed"] else "未完成"
            print(f"✅ 已将该待办标记为【{status}】")
        else:
            print("❌ 输入的序号不存在！")
    except ValueError:
        print("❌ 请输入正确的数字序号！")
    time.sleep(1)

def delete_todo(todos):
    """删除今日指定任务 - 修复：同步删除总任务列表中的对应项"""
    if not todos:
        print("❌ 暂无待办事项，无需删除！1秒后返回菜单...")
        time.sleep(1)
        return
    try:
        num = int(input("请输入要删除的待办序号："))
        if 1 <= num <= len(todos):
            # 步骤1：获取全部任务
            all_todos = load_todos(False)
            # 步骤2：找到并删除对应任务
            target_task = todos[num-1]
            for i in range(len(all_todos)):
                if all_todos[i]["create_time"] == target_task["create_time"] and all_todos[i]["content"] == target_task["content"]:
                    del all_todos[i]
                    break
            # 步骤3：保存修改后的总列表
            save_todos(all_todos)
            print(f"✅ 已删除待办：{target_task['content']}")
        else:
            print("❌ 输入的序号不存在！")
    except ValueError:
        print("❌ 请输入正确的数字序号！")
    time.sleep(1)

def clear_today_todo():
    """清空今日所有任务，保留历史任务"""
    all_todos = load_todos(False)
    today = get_today_date()
    # 过滤掉今日任务，保留其他日期的历史任务
    remain_todos = [t for t in all_todos if t["task_date"] != today]
    if len(all_todos) == len(remain_todos):
        print("❌ 暂无今日待办事项，无需清空！1秒后返回菜单...")
        time.sleep(1)
        return
    confirm = input("⚠️ 确定要清空今日所有待办事项吗？(输入 y 确认)：").strip().lower()
    if confirm == "y":
        save_todos(remain_todos)
        print("✅ 已清空今日所有待办事项，历史任务已保留！")
    else:
        print("✅ 已取消清空操作")
    time.sleep(1)

def search_todo_by_date():
    """查询功能：输入yyyymmdd格式日期，查询该日期所有任务+按序号精准查找"""
    all_todos = load_todos(False)
    if not all_todos:
        print("❌ 暂无任何历史任务可查询！1秒后返回菜单...")
        time.sleep(1)
        return
    
    print("\n===== 📖 历史任务查询功能 (输入格式：yyyymmdd 如20260113) =====")
    date_input = input("请输入要查询的日期(纯数字yyyymmdd)：").strip()
    target_date = date_convert(date_input)
    
    if not target_date:
        print("❌ 日期格式错误！请输入8位纯数字，例如：20260113")
        time.sleep(2)
        return
    
    # 筛选指定日期的所有任务
    target_todos = [t for t in all_todos if t["task_date"] == target_date]
    if not target_todos:
        print(f"❌ {date_input}({target_date}) 该日期暂无任何任务！")
        time.sleep(2)
        return
    
    # 展示该日期的所有任务+序号
    print(f"\n✅ 共查询到 {date_input}({target_date}) 的任务 {len(target_todos)} 条：")
    for index, todo in enumerate(target_todos, start=1):
        status = "✅ 已完成" if todo["completed"] else "❌ 未完成"
        content = todo["content"]
        create_time = todo["create_time"]
        print(f"    查询序号 {index}. {status} | {content} | 添加于：{create_time}")
    
    # 精准按序号查询单条详情
    try:
        print("\n———— 精准查询 ————")
        num = int(input("输入查询序号查看单条详情(输入0退出查询)："))
        if num == 0:
            print("✅ 退出查询功能")
            time.sleep(1)
            return
        if 1 <= num <= len(target_todos):
            todo = target_todos[num-1]
            status = "✅ 已完成" if todo["completed"] else "❌ 未完成"
            print(f"\n✨ 精准查询结果：")
            print(f"日期：{date_input}({target_date})")
            print(f"状态：{status}")
            print(f"内容：{todo['content']}")
            print(f"添加时间：{todo['create_time']}")
        else:
            print("❌ 输入的查询序号不存在！")
    except ValueError:
        print("❌ 请输入正确的数字序号！")
    
    input("\n查询完成，按回车键返回菜单...")

def main():
    """主程序入口 - 菜单新增【修改历史任务状态】选项"""
    # 启动实时时间线程
    t = threading.Thread(target=time_update_thread, daemon=True)
    t.start()
    time.sleep(0.1)
    
    while True:
        # 每次循环都重新加载今日任务，确保数据最新
        todos = load_todos(True)
        show_todos(todos)
        print("\n【⚙️ 操作菜单】")
        print("1. 添加今日待办事项")
        print("2. 编辑修改今日任务")
        print("3. 修改昨日/历史任务内容")
        print("4. 修改历史任务完成状态")
        print("5. 标记今日任务完成/未完成")
        print("6. 删除指定今日任务")
        print("7. 清空今日所有待办")
        print("8. 查询历史任务 (输入yyyymmdd日期)")
        print("0. 退出程序")
        choice = input("\n请输入操作编号(0-8)：").strip()
        
        if choice == "0":
            os.system('cls' if os.name == 'nt' else 'clear')
            print("=" * 65)
            print("        👋 感谢使用 Todo List，下次再见！")
            print("=" * 65)
            break
        elif choice == "1":
            add_todo(todos)
        elif choice == "2":
            edit_todo(todos)
        elif choice == "3":
            edit_history_todo_content()
        elif choice == "4":
            edit_history_todo_status()
        elif choice == "5":
            complete_todo(todos)
        elif choice == "6":
            delete_todo(todos)
        elif choice == "7":
            clear_today_todo()
        elif choice == "8":
            search_todo_by_date()
        else:
            print("❌ 输入错误，请输入0-8的数字！1秒后返回菜单...")
            time.sleep(1)

if __name__ == "__main__":
    main()