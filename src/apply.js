const { chromium } = require("playwright");
const readline = require("readline");

// 從環境變數讀取資料，如果沒有則預設讀取本地 application.json (相容舊用法)
const data = process.env.APPLICATION_DATA 
  ? JSON.parse(process.env.APPLICATION_DATA) 
  : require("./application.json");

async function promptUserInput(promptText) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  return new Promise((resolve) => {
    rl.question(promptText, (answer) => {
      console.log(promptText, answer);
      rl.close();
      resolve(answer);
    });
  });
}

async function apply() {
  const { org, route, destination, numOfDays, plan, members, watcher } = data;
  const isYushan = org === "玉山國家公園管理處";
  let { startDate } = data;

  const leader = members.find(({ leader }) => leader);
  const membersWithoutLeader = members.filter(({ leader }) => !leader);

  const browser = await chromium.launch({
    headless: false,
    args: ["--start-maximized"],
  });
  const context = await browser.newContext({
    viewport: null,
  });
  const page = await context.newPage();
  page.once("dialog", (dialog) => {
    console.log(`Dialog message: ${dialog.message()}`);
    dialog.dismiss().catch(() => {});
  });

  /**
   *
   */
  await page.goto("https://hike.taiwan.gov.tw/apply_1.aspx");
  await page.getByRole("button", { name: org }).click();
  const container = await page.getByText(route, { exact: true }).locator("..").locator("..");
  await container.getByRole("link", { name: "進入申請" }).click();

  /**
   *
   */
  /**
   * 自動勾選頁面上所有可見的條款勾選框
   */
  await page.waitForTimeout(500); // 稍微等待確保勾選框載入
  const checkboxes = await page.getByRole("checkbox").all();
  for (const checkbox of checkboxes) {
    if (await checkbox.isVisible()) {
      await checkbox.check().catch(() => {});
    }
  }
  await page.getByRole("button", { name: "同意", exact: true }).click();

  /**
   *
   */
  await page
    .getByRole("textbox", { name: isYushan ? "隊名" : "隊伍名稱" })
    .fill(`${leader.name}-${route}-${startDate}-${numOfDays}days`);

  await page.locator("#con_sumday").selectOption(String(numOfDays));
  await page.locator("#con_applystart").selectOption(startDate);
  for (let i = 0; i < plan.length; i++) {
    const day = plan[i];
    if (i > 0) await page.getByText(`第${i + 1}天行程`).waitFor({ state: "visible" });
    for (const spot of day.spots) {
      await page.getByRole("radio", { name: new RegExp(spot, "i") }).check();
    }
    await page.waitForTimeout(1000);
    await page.getByRole("link", { name: "  完成路線" }).click();
  }
  await page.getByText("請選擇下一個地點：").waitFor({ state: "hidden" });
  if (destination) await page.locator("#con_NpaPlacesInfo").selectOption(destination);
  await page.getByRole(isYushan ? "link" : "button", { name: "下一步" }).click();

  /**
   *
   */
  await page
    .getByRole("checkbox", {
      name: "請確認領隊或隊員同意委託申請人代理蒐集當事人個人資料，並委託其上網向國家公園管理處提出登山申請相關事宜，以免違反相關法令。",
    })
    .check();
  await page.getByRole("textbox", { name: isYushan ? "請輸入姓名" : "申請人姓名" }).fill(leader.name);
  await page
    .getByRole("textbox", { name: isYushan ? "請輸入電話" : "申請人電話" })
    .fill(leader.homePhone || leader.mobilePhone);
  await page.locator("#con_ddlapply_country").selectOption({ label: leader.city });
  await page.locator("#con_ddlapply_city").selectOption({ label: leader.district });
  await page.getByRole("textbox", { name: isYushan ? "請輸入地址" : "申請人地址" }).fill(leader.addressDetail);
  await page.getByRole("textbox", { name: isYushan ? "請輸入手機" : "申請人手機" }).fill(leader.mobilePhone);
  await page.getByRole("textbox", { name: isYushan ? "請輸入電子郵件" : "申請人電子郵件" }).fill(leader.email);
  // await page.waitForLoadState("networkidle");
  await page.getByRole("textbox", { name: isYushan ? "請輸入證號" : "申請人證號" }).fill(leader.idNumber);
  await page.evaluate(
    ({ leader }) => {
      document.querySelector('input[name="ctl00$con$apply_birthday"]').value = leader.birthday;
    },
    { leader }
  );
  await page.getByRole("textbox", { name: "緊急聯絡人姓名" }).fill(leader.emergencyContactName);
  await page.getByRole("textbox", { name: "緊急聯絡人電話" }).fill(leader.emergencyContactPhone);
  await page.locator("#con_apply_sex").selectOption("男");
  await page.locator("#con_apply_nation").selectOption("中華民國");
  /**
   *
   */
  await page.getByRole("button", { name: "   領隊資料(請展開填寫資料)" }).click();
  await page.getByRole("checkbox", { name: "同申請人" }).check();

  /**
   *
   */
  if (membersWithoutLeader.length > 0) {
    await page.getByRole("button", { name: "   隊員資料(請展開填寫資料)" }).click();
    if (!isYushan) await page.locator("#con_member_keytype").check();
    await page.waitForLoadState("networkidle");
  }
  for (let i = 0; i < membersWithoutLeader.length; i++) {
    const {
      name,
      homePhone,
      mobilePhone,
      email,
      city,
      district,
      addressDetail,
      idNumber,
      emergencyContactName,
      emergencyContactPhone,
      birthday,
    } = membersWithoutLeader[i];
    const label = `No.${i + 1}隊員資料`;
    await page.getByRole("link", { name: new RegExp("新增隊員", "i") }).click();
    await page.getByRole("button", { name: new RegExp(label, "i") }).click();
    await page.getByLabel(label).getByRole("textbox", { name: "請輸入姓名" }).fill(name);
    await page.locator(`#con_lisMem_ddlmember_country_${i}`).selectOption({ label: city });
    await page.locator(`#con_lisMem_ddlmember_city_${i}`).selectOption({ label: district });
    await page.getByLabel(label).getByRole("textbox", { name: "請輸入地址" }).fill(addressDetail);
    if (homePhone) await page.getByLabel(label).getByRole("textbox", { name: "請輸入電話" }).fill(homePhone);
    await page.getByLabel(label).getByRole("textbox", { name: "請輸入手機" }).fill(mobilePhone);
    await page.getByLabel(label).getByRole("textbox", { name: "請輸入電子郵件" }).fill(email);
    await page.getByLabel(label).getByPlaceholder("請輸入證號").fill(idNumber);
    await page.locator(`#con_lisMem_member_sex_${i}`).selectOption("男");
    await page.evaluate(
      ({ i, birthday }) => {
        document.querySelector(`input[name="ctl00$con$lisMem$ctrl${i + 1}$member_birthday"]`).value = birthday;
      },
      { i, birthday }
    );
    await page.getByLabel(label).getByRole("textbox", { name: "緊急聯絡人姓名" }).fill(emergencyContactName);
    await page.getByLabel(label).getByRole("textbox", { name: "緊急聯絡人電話" }).fill(emergencyContactPhone);
    await page.locator(`#con_lisMem_member_nation_${i}`).selectOption("中華民國");
  }

  /**
   *
   */
  await page.waitForTimeout(200);
  await page.getByRole("button", { name: "   留守人資料(請展開填寫資料)" }).click();
  await page
    .getByLabel("留守人資料(請展開填寫資料)")
    .getByRole("textbox", { name: isYushan ? "請輸入姓名" : "留守人手機" })
    .fill(watcher.name);
  await page
    .getByLabel("留守人資料(請展開填寫資料)")
    .getByRole("textbox", { name: isYushan ? "請輸入手機(或電話)" : "留守人手機" })
    .fill(watcher.mobilePhone);
  if (!isYushan) await page.getByRole("textbox", { name: "留守人電話" }).fill(watcher.homePhone || watcher.mobilePhone);
  await page.locator("#con_stay_email").fill(watcher.email);
  await page.evaluate(
    ({ watcher }) => {
      document.querySelector('input[name="ctl00$con$stay_birthday"]').value = watcher.birthday;
    },
    { watcher }
  );

  /**
   *
   */
  try {
    await page.locator("#con_cbOneMan").check();
  } catch (error) {}
  await page.locator("#con_btnToStep31").click();
  // await page.evaluate(() => {
  //   document.documentElement.style.transform = "scale(0.5)";
  //   document.documentElement.style.transformOrigin = "top left";
  // });
}

apply().catch(console.error);
