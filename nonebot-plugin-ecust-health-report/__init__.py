from playwright.async_api import Playwright, async_playwright
from playwright._impl._api_types import TimeoutError as Terror
from nonebot import on_command, get_bot
from nonebot.params import CommandArg, Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent, Event
from nonebot_plugin_apscheduler import scheduler
from nonebot.permission import SUPERUSER
from .sql import add_school_account, get_school_account, delete_school_account
import asyncio


register = on_command('健康打卡', priority=16, block=True)
stop = on_command('停止健康打卡', priority=16, block=True)
go = on_command('强制健康打卡', permission=SUPERUSER)


@register.handle()
async def reg(event: PrivateMessageEvent, msg: Message = CommandArg()):
    uid = event.get_user_id()
    args_ls = msg.extract_plain_text().strip().split()
    if len(args_ls) != 2:
        await register.finish('参数错误，请在指令后加上学号 密码')
    if len(args_ls[0]) != 8:
        await register.finish('学号长度错误，请重试')
    add_school_account(uid, args_ls[0], args_ls[1])
    await register.finish(f'绑定成功,将在1点自动打卡\n请确认你的账号\n学号:{args_ls[0]}\n密码:{args_ls[1]}\n有误请发送 /停止健康打卡')


@register.handle()
async def _reg(event: GroupMessageEvent):
    await register.finish(f'请私聊使用本功能')


@stop.handle()
async def _(event: Event):
    uid = event.get_user_id()
    try:
        delete_school_account(uid)
    except Exception:
        await stop.finish('你目前还没注册过健康打卡 发送/健康打卡 学号 密码 来自动打卡')
    await stop.finish('已停止自动健康打卡')


@scheduler.scheduled_job("cron", hour="15", minute="55", max_instances=10, misfire_grace_time=10)
@go.handle()
async def _():
    data = get_school_account()
    for uid, account, password in data:
        try:
            async with async_playwright() as playwright:
                await run(playwright, account, password)
        except Terror:
            msg = '健康打卡失败，可能已自行打卡，请注意需自行填写'
        except Exception as e:
            msg = f'健康打卡失败 错误原因{e}'
        else:
            msg = '今日已完成健康打卡'
        try:
            bot = get_bot()
            await bot.send_private_msg(user_id=int(uid), message=msg)
        except ValueError:
            continue
        await asyncio.sleep(2)


async def run(playwright: Playwright, stu_id, password) -> None:
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    # Open new page
    page = await context.new_page()
    await page.goto(
        "https://sso.ecust.edu.cn/authserver/login?service=https%3A%2F%2Fworkflow.ecust.edu.cn%2Fdefault%2Fwork%2Fuust%2Fzxxsmryb%2Fmrybcn.jsp")
    # Click [placeholder="用户名"]
    await page.click("[placeholder=\"用户名\"]")
    # Fill [placeholder="用户名"]
    await page.fill("[placeholder=\"用户名\"]", stu_id)
    # Click [placeholder="密码"]
    await page.click("[placeholder=\"密码\"]")
    # Fill [placeholder="密码"]
    await page.fill("[placeholder=\"密码\"]", password)
    # Click button:has-text("登录")
    await page.click("button:has-text(\"登录\")")
    # assert page.url == "https://workflow.ecust.edu.cn/default/work/uust/zxxsmryb/mrybcn.jsp"
    # Click ins
    await page.click("ins")
    # Click text=下一步
    await page.click("text=下一步")
    await page.click("label:has-text(\"健康\")")
    # Click #radio_sfycxxwc34
    await page.click("#radio_sfycxxwc34")
    # Click text=*行程码是否绿码： 是否 >> ins
    await page.click("#radio_xcm5")
    # Click text=提交
    await page.click("text=提交")
    # Click text=确定
    await page.click("text=确定")
    # Click text=确定
    await page.click("text=确定")
    # ---------------------
    await context.close()
    await browser.close()
