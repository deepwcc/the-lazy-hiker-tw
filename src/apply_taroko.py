import os
import json
import yaml
import asyncio
import sys
import re
from playwright.async_api import async_playwright

async def check_page_errors(page):
    # 檢查是否有顯眼的錯誤訊息文字
    error_selectors = [
        ".error-message",
        ".alert-danger",
        "#error_msg",
        "[id*='lblError']",
        "[id*='ErrorMessage']",
    ]
    
    for selector in error_selectors:
        try:
            locator = page.locator(selector)
            if await locator.is_visible():
                text = await locator.inner_text()
                if text and text.strip():
                    print(f"[Error] 網頁顯示錯誤訊息: {text}", file=sys.stderr)
                    return True
        except:
            pass
    return False

async def apply(data=None, test_mode=None):
    # 如果沒有傳入 data，則嘗試從環境變數或本地檔案讀取
    if data is None:
        data_str = os.environ.get("APPLICATION_DATA")
        if data_str:
            try:
                data = yaml.safe_load(data_str)
            except:
                data = json.loads(data_str)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
            # 優先找 yaml
            for ext in ["yaml", "yml", "json"]:
                path = os.path.join(base_path, f"application.{ext}")
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        if ext in ["yaml", "yml"]:
                            data = yaml.safe_load(f)
                        else:
                            data = json.load(f)
                    break
            if not data:
                data = {}

    # 如果沒有傳入 test_mode，則從環境變數讀取
    if test_mode is None:
        test_mode = os.environ.get("TEST_MODE") == "true"

    org = data.get("org")
    route = data.get("route")
    destination = data.get("destination")
    num_of_days = data.get("numOfDays")
    plan = data.get("plan", [])
    watcher = data.get("watcher", {})
    leader = data.get("leader", {})
    members_without_leader = data.get("members", [])
    start_date = data.get("startDate")
    
    is_yushan = org == "玉山國家公園管理處"
    
    # 如果 leader 是空的，嘗試從 members 找 (相容舊格式)
    if not leader and members_without_leader:
        leader = next((m for m in members_without_leader if m.get("leader")), None)
        members_without_leader = [m for m in members_without_leader if not m.get("leader")]
    
    if not leader:
        leader = {}

    has_dialog = False
    has_page_error = False
    current_step = "初始化"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=["--start-maximized"])
        context = await browser.new_context(no_viewport=True)
        page = await context.new_page()

        def handle_dialog(dialog):
            nonlocal has_dialog, current_step
            msg = dialog.message
            if "請詳實填寫隊員資料勿重覆" in msg:
                print(f"[Warning] 網頁彈出對話框 (已略過): {msg}", file=sys.stderr)
            else:
                print(f"[Error] 在「{current_step}」時彈出對話框: {msg}", file=sys.stderr)
                has_dialog = True
            asyncio.create_task(dialog.dismiss())

        page.on("dialog", handle_dialog)

        # 1. 進入申請頁面
        current_step = "進入申請頁面"
        await page.goto("https://hike.taiwan.gov.tw/apply_1.aspx")
        await page.get_by_role("button", name=org).click()
        
        # 尋找路線並點擊進入申請
        current_step = f"尋找路線並進入申請: {route}"
        container = page.get_by_text(route, exact=True).locator("..").locator("..")
        await container.get_by_role("link", name="進入申請").click()
        if await check_page_errors(page):
            has_page_error = True

        # 2. 同意條款
        current_step = "同意條款"
        await asyncio.sleep(0.5)
        checkboxes = await page.get_by_role("checkbox").all()
        for checkbox in checkboxes:
            if await checkbox.is_visible():
                try:
                    await checkbox.check()
                except:
                    pass
        await page.get_by_role("button", name="同意", exact=True).click()
        if await check_page_errors(page):
            has_page_error = True

        # # 3. 填寫行程資料
        # current_step = "填寫行程資料 - 隊伍名稱"
        # team_name_label = "隊名" if is_yushan else "隊伍名稱"
        # await page.get_by_role("textbox", name=team_name_label).fill(
        #     f"{leader['name']}-{route}-{start_date}-{num_of_days}days"
        # )

        await page.locator("#con_step1_noteCheck_CheckBox").check(force=True)

        current_step = "填寫行程資料 - 天數與日期"
        await page.locator("#con_step1_sumday").select_option(str(num_of_days))
        await page.locator("#con_step1_applystart").select_option(start_date)
        # await asyncio.sleep(0.5);
        # await page.locator("#con_step1_noteCheck_CheckBox").check(force=True)

        for i, day in enumerate(plan):
            current_step = f"填寫行程資料 - 第 {i+1} 天行程"
            # print(current_step)
            if i > 0:
                await page.get_by_text(f"第：{i + 1}天行程").wait_for(state="visible")
            # print(current_step)
            for spot in day.get("spots", []):
                # print(spot)
                await page.get_by_role("radio", name=re.compile(spot, re.IGNORECASE)).check()
                await asyncio.sleep(0.5)
            # print("---")
            await asyncio.sleep(0.5)
            await page.get_by_role("link", name="  完成路線").click()
        
        current_step = "填寫行程資料 - 選擇目的地"
        await page.get_by_text("請選擇下一個地點：").wait_for(state="hidden")
        if destination:
            await page.locator("#con_NpaPlacesInfo").select_option(destination)
        
        current_step = "填寫行程資料 - 點擊下一步"
        next_step_role = "link" if is_yushan else "button"
        await asyncio.sleep(0.5)
        # input("請按 Enter 鍵繼續...") # for debug
        await page.get_by_role(next_step_role, name="下一步").click()
        await asyncio.sleep(0.5)
        if await check_page_errors(page):
            has_page_error = True

        # 4. 填寫申請人與領隊資料
        current_step = "填寫申請人資料 - 同意委託"
        await page.get_by_role("checkbox", name="請確認領隊或隊員同意委託申請人代理蒐集當事人個人資料，並委託其上網向國家公園管理處提出登山申請相關事宜，以免違反相關法令。").check()
        
        name_label = "請輸入姓名"
        phone_label = "請輸入電話"
        addr_label = "請輸入地址"
        mobile_label = "請輸入手機"
        email_label = "請輸入電子郵件"

        current_step = "填寫申請人資料 - 基本欄位"
        await page.get_by_role("textbox", name=name_label).fill(leader['name'])
        await page.get_by_role("textbox", name=phone_label).fill(leader.get('homePhone') or leader['mobilePhone'])
        await page.locator("#con_step2_ddlapply_country").select_option(label=leader['city']) #ctl00$con$step2$ddlapply_country
        await page.locator("#con_step2_ddlapply_city").select_option(label=leader['district']) #ctl00$con$step2$ddlapply_city
        await page.get_by_role("textbox", name=addr_label).fill(leader['addressDetail'])
        await page.get_by_role("textbox", name=mobile_label).fill(leader['mobilePhone'])
        await page.get_by_role("textbox", name=email_label).fill(leader['email'])
        await page.locator("#con_step2_apply_nation").select_option("中華民國") #ctl00$con$step2$apply_nation
        await asyncio.sleep(0.5)
        
        current_step = "填寫申請人資料 - 身分證字號"
        await page.locator("#con_step2_apply_sid").fill(leader['idNumber']) #ctl00$con$step2$apply_sid
        await page.locator("#con_step2_apply_sid").press("Tab") #ctl00$con$step2$apply_sid

        current_step = "填寫申請人資料 - 性別與生日"
        try:
            gender = "男" if leader['idNumber'][1] == '1' else "女"
            await page.locator("#con_step2_apply_sex").select_option(label=gender) #ctl00$con$step2$apply_sex
        except Exception as e:
            print(f"無法選取性別: {e}")
        await asyncio.sleep(0.5)
        
        # 使用 evaluate 設定生日並觸發事件
        await page.evaluate(
            """(args) => {
                const el = document.querySelector('input[name="ctl00$con$step2$apply_birthday"]');
                if (el) {
                    el.value = args.birthday;
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                    el.dispatchEvent(new Event('blur', { bubbles: true }));
                }
            }""",
            {"birthday": leader['birthday']}
        )
        await asyncio.sleep(0.5)
        
        await page.get_by_role("textbox", name="緊急聯絡人姓名").fill(leader['emergencyContactName'])
        await asyncio.sleep(0.5)
        await page.get_by_role("textbox", name="緊急聯絡人電話").fill(leader['emergencyContactPhone'])
        await asyncio.sleep(0.5)
        
        current_step = "填寫領隊資料 - 展開並勾選同申請人"
        await page.get_by_role("button", name=" 領隊資料 (請展開填寫資料)").click()
        await page.get_by_role("checkbox", name="同申請人").check()

        # input("請按 Enter 鍵繼續...") # for debug

        # 5. 填寫隊員資料
        if members_without_leader:
            current_step = "填寫隊員資料 - 展開區塊"
            await page.get_by_role("button", name=" 隊員資料 (請展開填寫資料)").click()
            if not is_yushan:
                await page.locator("#con_step2_member_keytype").check()
            await page.wait_for_load_state("networkidle")

            # <span style="color: #0000cc;">請確認領隊或隊員同意委託申請人代理蒐集當事人個人資料，並委託其上網向國家公園管理處提出登山申請，以免違反相關法令。</span>
            # await page.locator("#con_step2_member_keytype").wait_for(state="visible");
            # await page.locator("#con_step2_member_keytype").check(force=True)
            # input("請按 Enter 鍵繼續...") # for debug
            
            for i, member in enumerate(members_without_leader):
                label = f"No.{i + 1}隊員資料"
                current_step = f"填寫隊員資料 - 新增第 {i+1} 位隊員"
                await page.get_by_role("link", name=re.compile("新增隊員", re.IGNORECASE)).click()
                await asyncio.sleep(1) # 等待網頁產生新欄位
                # await page.get_by_role("button", name=re.compile(label, re.IGNORECASE)).click()

                # member_section = page.get_by_label(label)
                # # 等待區塊可見再開始填寫
                # await member_section.wait_for(state="visible", timeout=5000)

                current_step = f"填寫隊員資料 - 填寫第 {i+1} 位隊員基本欄位"
                await page.locator(f"#con_step2_lisMem_member_name_{i}").fill(member['name']) # id=con_step2_lisMem_member_name_0
                await asyncio.sleep(0.5)
                await page.locator(f"#con_step2_lisMem_member_tel_{i}").fill(member['mobilePhone']) # id=con_step2_lisMem_member_tel_0
                await asyncio.sleep(0.5)
                await page.locator(f"#con_step2_lisMem_ddlmember_country_{i}").select_option(label=member['city']) # id=con_step2_lisMem_ddlmember_country_0
                await asyncio.sleep(0.5)
                await page.locator(f"#con_step2_lisMem_ddlmember_city_{i}").select_option(label=member['district']) # id=con_step2_lisMem_ddlmember_city_0
                await asyncio.sleep(0.5)
                await page.locator(f"#con_step2_lisMem_member_addr_{i}").fill(member['addressDetail']) # id=con_step2_lisMem_member_addr_0
                await asyncio.sleep(0.5)
                await page.locator(f"#con_step2_lisMem_member_mobile_{i}").fill(member['mobilePhone']) # id=con_step2_lisMem_member_tel_0
                await asyncio.sleep(0.5)
                await page.locator(f"#con_step2_lisMem_member_email_{i}").fill(member['email']) # id=con_step2_lisMem_member_email_0
                await asyncio.sleep(0.5)
                await page.locator(f"#con_step2_lisMem_member_nation_{i}").select_option("中華民國") # con_step2_lisMem_member_nation_0
                await asyncio.sleep(0.5)
                
                current_step = f"填寫隊員資料 - 填寫第 {i+1} 位隊員身分證字號"
                await page.locator(f"#con_step2_lisMem_member_sid_{i}").fill(member['idNumber']) # con_step2_lisMem_member_sid_0
                await page.locator(f"#con_step2_lisMem_member_sid_{i}").press("Tab") #ctl00$con$step2$member_sid_{i}

                current_step = f"填寫隊員資料 - 填寫第 {i+1} 位隊員性別與生日"
                try:
                    gender = "男" if member['idNumber'][1] == '1' else "女"
                    await page.locator(f"#con_step2_lisMem_member_sex_{i}").select_option(label=gender) # con_step2_lisMem_member_sex_0
                except Exception as e:
                    print(f"無法選取隊員 {i+1} 性別: {e}")
                
                # 使用 evaluate 設定生日並觸發事件
                await page.evaluate(
                    """(args) => {
                        const el = document.querySelector(`input[name="ctl00$con$step2$lisMem$ctrl${args.i + 1}$member_birthday"]`);
                        if (el) {
                            el.value = args.birthday;
                            el.dispatchEvent(new Event('change', { bubbles: true }));
                            el.dispatchEvent(new Event('blur', { bubbles: true }));
                        }
                    }""",
                    {"i": i, "birthday": member['birthday']}
                )
                await asyncio.sleep(0.5)
                
                current_step = f"填寫隊員資料 - 填寫第 {i+1} 位隊員緊急聯絡人"
                # await member_section.get_by_role("textbox", name="緊急聯絡人姓名").fill(member['emergencyContactName'])
                await page.locator(f"#con_step2_lisMem_member_contactname_{i}").fill(member['emergencyContactName']) # id=con_step2_lisMem_member_contactname_0
                await asyncio.sleep(0.5)
                await page.locator(f"#con_step2_lisMem_member_contacttel_{i}").fill(member['emergencyContactPhone'])
                await asyncio.sleep(0.5)
                # input("請按 Enter 鍵繼續...") # for debug

        # 6. 填寫留守人資料
        current_step = "填寫留守人資料 - 展開區塊"
        await asyncio.sleep(0.5)
        await page.get_by_role("button", name="留守人資料 (請展開填寫資料)").click()
        await asyncio.sleep(0.5)
        watcher_section = page.get_by_label("留守人資料 (請展開填寫資料)")
        await asyncio.sleep(0.5)
        
        current_step = "填寫留守人資料 - 基本欄位"
        # watcher_name_label = "請輸入姓名" if is_yushan else "留守人姓名"
        await watcher_section.locator("#con_step2_stay_name").fill(watcher['name']) #con_step2_stay_name
        
        # watcher_mobile_label = "請輸入手機(或電話)" if is_yushan else "留守人手機"
        await watcher_section.locator("#con_step2_stay_mobile").fill(watcher['mobilePhone']) #con_step2_stay_mobile
        
        # if not is_yushan:
        await watcher_section.locator("#con_step2_stay_tel").fill(watcher.get('homePhone') or watcher['mobilePhone']) #con_step2_stay_tel
        
        current_step = "填寫留守人資料 - Email 與生日"
        await watcher_section.locator("#con_step2_stay_email").fill(watcher['email']) #con_step2_stay_email
        # await page.locator("#con_step2_stay_email").press("Tab") #con_step2_stay_email
        
        # await page.evaluate(
        #     """(watcher) => {
        #         const el = document.querySelector('input[name="ctl00$con$stay_birthday"]');
        #         if (el) {
        #             el.value = watcher.birthday;
        #             el.dispatchEvent(new Event('change', { bubbles: true }));
        #             el.dispatchEvent(new Event('blur', { bubbles: true }));
        #         }
        #     }""",
        #     watcher
        # )
        # await page.locator('input[name="ctl00$con$stay_birthday"]').press("Tab")

        current_step = "留守人填寫完成"
        if test_mode:
            print("🧪 測試模式：填寫完成，自動關閉瀏覽器")
            await browser.close()
            return has_dialog, has_page_error

        # 7. 最後步驟
        current_step = "最後步驟 - 勾選聲明並點擊完成"
        try:
            await page.locator("#con_cbOneMan").check()
        except:
            pass
        
        await page.locator("#con_btnToStep31").click()
        await asyncio.sleep(0.5)
        if await check_page_errors(page):
            has_page_error = True

        print("\n✅ 自動填寫完成！請手動檢查資料、輸入驗證碼並提交。")
        print("💡 提示：手動關閉瀏覽器後，程式才會正式結束。")
        try:
            # 保持瀏覽器開啟，直到頁面關閉
            await page.wait_for_event("close", timeout=0)
        except:
            pass

    return has_dialog, has_page_error

if __name__ == "__main__":
    try:
        has_dialog, has_page_error = asyncio.run(apply())
        if has_dialog or has_page_error:
            print("❌ 執行過程中出現對話框或網頁錯誤，視為失敗。", file=sys.stderr)
            sys.exit(1)
        sys.exit(0)
    except Exception as e:
        print(f"執行過程中發生錯誤: {e}", file=sys.stderr)
        sys.exit(1)
