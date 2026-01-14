import os
import time
import datetime
import threading
import configparser

# ========== 核心配置 - 无改动 ==========
TODO_FILE = "todo_list.txt"
CONFIG_FILE = "todo_config.configrecorderPythonTodo"  # 专属后缀配置文件
current_time_str = ""
ADMIN_PASSWORD = "sun130202"
STATUS_MAP = {
    0: ("❌ 未完成", "未完成"),
    1: ("✅ 已完成", "已完成"),
    2: ("⚡ 进行中", "进行中"),
    3: ("❓ 未知", "未知")
}
STATUS_TIPS = "状态量说明：0=未完成、1=已完成、2=进行中、3=未知"

# ========== 所有功能开关列表（全部可控，顺序和截图一致） ==========
FUNCTIONS = {
    "add_todo": "添加今日待办事项",
    "edit_todo": "编辑修改今日任务",
    "edit_history_content": "修改昨日/历史任务内容",
    "edit_history_status": "修改历史任务状态【输0/1/2/3】",
    "edit_today_status": "修改今日任务状态【输0/1/2/3】",
    "delete_todo": "删除指定今日任务",
    "clear_today": "清空今日所有待办",
    "search_todo": "查询历史任务（输入日期）",
    "admin_entrance": "🔐 管理员调试入口"
}

# ========== 配置文件初始化与读写 ==========
def init_config():
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        config["FUNCTION_SWITCH"] = {func: "1" for func in FUNCTIONS.keys()}
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            config.write(f)
    config.read(CONFIG_FILE, encoding="utf-8")
    return config

def get_func_status(func_name):
    config = init_config()
    return config.get("FUNCTION_SWITCH", func_name, fallback="1") == "1"

def set_func_status(func_name, status):
    config = init_config()
    config["FUNCTION_SWITCH"][func_name] = "1" if status else "0"
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        config.write(f)

# ========== 时间相关函数 ==========
def get_format_time():
    week_dict = {0: "周一", 1: "周二", 2: "周三", 3: "周四", 4: "周五", 5: "周六", 6: "周日"}
    now = datetime.datetime.now()
    week_num = now.weekday()
    return now.strftime(f"%Y-%m-%d %H:%M:%S {week_dict[week_num]}")

def get_today_date():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def get_today_date_yyyymmdd():
    return datetime.datetime.now().strftime("%Y%m%d")

def get_yesterday_date_yyyymmdd():
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    return yesterday.strftime("%Y%m%d")

def date_convert(ymd_str):
    if len(ymd_str) == 8 and ymd_str.isdigit():
        return f"{ymd_str[:4]}-{ymd_str[4:6]}-{ymd_str[6:8]}"
    return ""

# ========== 任务加载与保存 ==========
def load_todos(is_today_only=True):
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
    with open(TODO_FILE, "w", encoding="utf-8") as f:
        for todo in todos:
            f.write(f"{todo['status']}|{todo['content']}|{todo['create_time']}\n")

# ========== 实时时间线程 ==========
def time_update_thread():
    global current_time_str
    while True:
        current_time_str = get_format_time()
        time.sleep(1)

# ========== 任务展示 ==========
def show_todos(todos):
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 70)
    print("        📋 Python Todo List (修复版-全功能可控)")
    print("=" * 70)
    today = get_today_date()
    print(f"\n📅 今日日期：{today} ({get_today_date_yyyymmdd()}) | 昨日日期：{get_yesterday_date_yyyymmdd()}")
    print(f"📌 {STATUS_TIPS}")
    
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

# ========== 核心功能函数（全部加开关校验，无改动） ==========
def add_todo(todos):
    if not get_func_status("add_todo"):
        print("❌ 该功能已被管理员关闭！1秒后返回菜单...")
        time.sleep(1)
        return
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
    if not get_func_status("edit_todo"):
        print("❌ 该功能已被管理员关闭！1秒后返回菜单...")
        time.sleep(1)
        return
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
    if not get_func_status("edit_history_content"):
        print("❌ 该功能已被管理员关闭！1秒后返回菜单...")
        time.sleep(1)
        return
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

def edit_history_todo_status():
    if not get_func_status("edit_history_status"):
        print("❌ 该功能已被管理员关闭！1秒后返回菜单...")
        time.sleep(1)
        return
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

def complete_todo(todos):
    if not get_func_status("edit_today_status"):
        print("❌ 该功能已被管理员关闭！1秒后返回菜单...")
        time.sleep(1)
        return
    if not todos:
        print("❌ 暂无今日任务！1秒后返回菜单...")
        time.sleep(1)
        return
    try:
        num = int(input("请输入要修改状态的任务序号："))
        if 1 <= num <= len(todos):
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
    if not get_func_status("delete_todo"):
        print("❌ 该功能已被管理员关闭！1秒后返回菜单...")
        time.sleep(1)
        return
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
    if not get_func_status("clear_today"):
        print("❌ 该功能已被管理员关闭！1秒后返回菜单...")
        time.sleep(1)
        return
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
    if not get_func_status("search_todo"):
        print("❌ 该功能已被管理员关闭！1秒后返回菜单...")
        time.sleep(1)
        return
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

# ========== 管理员功能（修复开关控制逻辑） ==========
def show_func_switch_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 60)
    print("        ⚙️  功能开关配置中心 | 管理员专属")
    print("=" * 60)
    print("\n当前功能开关状态：")
    for func_key, func_name in FUNCTIONS.items():
        status = "✅ 开启" if get_func_status(func_key) else "❌ 关闭"
        print(f"  {func_key:<20} {func_name:<25} {status}")
    print("\n操作说明：输入功能标识(如add_todo)切换开关，输入0返回管理员菜单")

def toggle_func_switch():
    show_func_switch_menu()
    while True:
        choice = input("\n请输入要切换的功能标识(输入0返回)：").strip()
        if choice == "0":
            return
        if choice in FUNCTIONS.keys():
            current_status = get_func_status(choice)
            set_func_status(choice, not current_status)
            new_status = "开启" if not current_status else "关闭"
            print(f"\n✅ 功能【{FUNCTIONS[choice]}】已{new_status}！")
            time.sleep(1)
            show_func_switch_menu()
        else:
            print("\n❌ 功能标识不存在！请重新输入")

def admin_entrance():
    if not get_func_status("admin_entrance"):
        print("❌ 管理员入口已被关闭！1秒后返回菜单...")
        time.sleep(1)
        return
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 60)
    print("        🔐 管理员调试入口 | 验证页面")
    print("=" * 60)
    input_pwd = input("\n请输入管理员密码：").strip()
    if input_pwd != ADMIN_PASSWORD:
        print(f"\n❌ 密码错误！请确认密码后重试")
        time.sleep(2)
        return
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=" * 60)
        print("        ✅ 管理员调试中心")
        print("=" * 60)
        print("1. 功能开关配置")
        print("0. 返回主程序菜单")
        choice = input("\n请输入操作序号：").strip()
        if choice == "0":
            return
        elif choice == "1":
            toggle_func_switch()
        else:
            print("❌ 输入错误！请输入0或1")
            time.sleep(1)

# ========== ✅ 核心修复：主程序入口（彻底重写菜单调用逻辑，无任何崩溃） ==========
def main():
    init_config()
    # 启动实时时间线程
    t = threading.Thread(target=time_update_thread, daemon=True)
    t.start()
    time.sleep(0.1)
    
    # 功能映射表：解决核心调用BUG
    func_action_map = {
        "add_todo": lambda: add_todo(todos),
        "edit_todo": lambda: edit_todo(todos),
        "edit_history_content": lambda: edit_history_todo_content(),
        "edit_history_status": lambda: edit_history_todo_status(),
        "edit_today_status": lambda: complete_todo(todos),
        "delete_todo": lambda: delete_todo(todos),
        "clear_today": lambda: clear_today_todo(),
        "search_todo": lambda: search_todo_by_date(),
        "admin_entrance": lambda: admin_entrance()
    }

    while True:
        todos = load_todos(True)
        show_todos(todos)
        print("\n【⚙️  操作菜单 | 全功能开关已生效】")
        menu_list = []
        menu_idx = 1
        # 固定功能顺序，和截图一致
        func_order = ["add_todo", "edit_todo", "edit_history_content", "edit_history_status", 
                      "edit_today_status", "delete_todo", "clear_today", "search_todo", "admin_entrance"]
        # 生成可用菜单
        for func_key in func_order:
            if get_func_status(func_key):
                print(f"{menu_idx}. {FUNCTIONS[func_key]}")
                menu_list.append(func_key)
                menu_idx += 1
        print(f"0. 退出程序")

        # 菜单选择与调用 - 加容错处理
        try:
            choice = input("\n请输入操作编号(0-{})：".format(len(menu_list))).strip()
            if not choice.isdigit():
                print("❌ 请输入有效的数字序号！")
                time.sleep(1)
                continue
            choice = int(choice)
            if choice == 0:
                os.system('cls' if os.name == 'nt' else 'clear')
                print("=" * 70)
                print("        👋 感谢使用 Todo List，下次再见！")
                print("=" * 70)
                break
            elif 1 <= choice <= len(menu_list):
                target_func = menu_list[choice-1]
                func_action_map[target_func]() # 安全调用功能，无任何崩溃
            else:
                print(f"❌ 输入错误！请输入0-{len(menu_list)}的数字")
                time.sleep(1)
        except Exception as e:
            print(f"❌ 操作出错，自动重试！错误信息：{str(e)}")
            time.sleep(2)

if __name__ == "__main__":
    main()