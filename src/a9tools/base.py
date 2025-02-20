import json
import os
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from typing import List, Optional
from urllib.parse import urlparse, parse_qs

import requests
from DrissionPage import ChromiumOptions, ChromiumPage
from DrissionPage._pages.chromium_tab import ChromiumTab
from fake_useragent import UserAgent

from .fingerprint import random_fingerprint, FingerprintModel
from .log import logger
from .model import InputInfoBase
from .utils import get_2fa_code


class HandlerBase(ABC):
    def __init__(
        self,
        wallet_info_path: str | InputInfoBase,
        auto_load_extension: bool = True,
        fingerprint_info_path: Optional[str] = None,
    ) -> None:
        """
        user_data_path: 用户数据目录
        auto_load_extension: 是否自动加载 extensions 目录下的所有插件
        fingerprint_info_path: fingerprint.json 的路径
        """
        if isinstance(wallet_info_path, InputInfoBase):
            self.input_info = wallet_info_path
        else:
            self.input_info = self._load_input(wallet_info_path)
        logger.info(f"浏览器数据目录 {self.input_info.user_data_path}")
        if not fingerprint_info_path:
            fingerprint_info_path = os.path.join(
                self.input_info.user_data_path, "fingerprint.json"
            )

        self.fingerprint_info_path = fingerprint_info_path

        self.opt = self.get_chrome_options(self.input_info.user_data_path)
        self.opt.set_timeouts(base=5)
        if auto_load_extension:
            self.__add_extension(self.opt)

    def _load_input(self, input_info: str) -> InputInfoBase:
        with open(input_info, "r") as f:
            data = json.load(f)
        return InputInfoBase.model_validate(data)

    def __init_user_data_info(self) -> ChromiumOptions:
        """
        初始化浏览器启动项
        """
        opt = ChromiumOptions()
        opt.set_argument("--lang", "en")
        opt.auto_port()
        opt.set_pref("credentials_enable_service", False)
        opt.set_pref("settings.language.preferred_languages", "en-US")
        opt.set_pref("intl.accept_languages", "en-US,en")
        opt.set_argument("--hide-crash-restore-bubble")
        ua = UserAgent(browsers=["chrome"], os=["macos", "windows"], min_version=120)
        user_agent = ua.getRandom
        logger.info(f"generate user agent {user_agent}")
        opt.set_user_agent(user_agent.get("useragent", ""))
        opt.set_user_data_path(self.input_info.user_data_path)
        self.__init_fingerpring(user_agent)
        return opt

    @abstractmethod
    def start_url(self) -> str:
        """
        返回项目的起始 url
        必须实现，初始化完指纹插件以后会自动打开这个地址
        """
        ...

    def get_chrome_options(self, user_data_path: str) -> ChromiumOptions:
        """
        根据传入的用户数据目录，初始化 ChromiumOptions
        """
        ini_path = f"{user_data_path}/config.ini"
        if os.path.exists(ini_path):
            opt = ChromiumOptions(ini_path=f"{user_data_path}/config.ini")
            self.__load_fingerpring()
        else:
            opt = self.__init_user_data_info()
        return opt

    @staticmethod
    def __add_extension(opt: ChromiumOptions) -> None:
        """
        加载插件
        """
        opt.remove_extensions()
        if os.path.exists("extensions"):
            extension_list = os.listdir("extensions")
            logger.info(f"incofing {opt.extensions}")
            for extension in extension_list:
                if os.path.isdir(os.path.join("extensions", extension)):
                    logger.info(f"加载插件 {extension}")
                    path_e = os.path.join("extensions", extension)
                    if path_e not in opt.extensions:
                        opt.add_extension(os.path.join("extensions", extension))
        else:
            tools = ["tools-extension", "webrtc-control"]
            for tool in tools:
                abspath = os.path.join(os.path.pardir, tool)
                path = os.path.abspath(abspath)
                opt.add_extension(path)

    def add_extension(self, extension_path: str) -> None:
        """
        添加插件
        """
        if extension_path not in self.opt.extensions:
            self.opt.add_extension(extension_path)

    def add_chrome_start_args(self, args: List[str] = []) -> None:
        """
        添加启动参数
        self.opt.add_argument("xxxxx")
        """
        for arg in args:
            self.opt.set_argument(arg)

    def _save_tools_extension_url(self, tab):
        """保存指纹插件的选项 url"""
        p = os.path.join(self.input_info.user_data_path, "tools_extension_url")
        with open(p, "w") as f:
            f.write(tab.url)

    def _get_tools_extension_url(self) -> str:
        """获取指纹插件的选项 url"""
        p = os.path.join(self.input_info.user_data_path, "tools_extension_url")
        with open(p, "r") as f:
            return f.read()

    def _check_a9tool_urls(self):
        for tab in self.driver.get_tabs():
            logger.info(f"_check_a9tool_urls title:{tab.title}")
            if tab.title == "A9Tools":
                logger.info("打开指纹插件 tab")
                self._save_tools_extension_url(tab)
                self._import_fingerprint_info(tab)
                self.driver.close_tabs(tab)
                return True
        return False

    def __init_fingerpring(self, ua: dict) -> None:
        chrome_version = ua.get("version", "")
        platform = ua.get("os", "")
        if platform.startswith("win"):
            platform = "windows"
        elif platform.startswith("mac"):
            platform = "macos"
        else:
            raise Exception(f"不支持的平台 {platform}")
        self.fingerprint = random_fingerprint(
            self.input_info.proxy_host,
            self.input_info.proxy_port,
            str(chrome_version),
            platform,
        )
        logger.info(self.fingerprint)

    def __load_fingerpring(self):
        with open(self.fingerprint_info_path, "r") as f:
            data = json.load(f)
        self.fingerprint = FingerprintModel.model_validate(data)
        logger.info(self.fingerprint)

    def init_driver(
        self, headless=False, with_metamask: bool = False, port: int = 9222
    ) -> None:
        """
        获取 Chrome 的操作 driver
        """
        if headless:
            self.opt.headless(True)
        else:
            self.opt.headless(False)
        if with_metamask:
            self.add_metamask_extension()
        # if self.input_info.proxy_host:
        #     self.opt.set_argument(
        #         "--proxy-server",
        #         f"http://{self.input_info.proxy_host}:{self.input_info.proxy_port}",
        #     )
        self.opt.set_local_port(port)
        self.opt.set_user_data_path(self.input_info.user_data_path)
        self.add_chrome_start_args()
        self.driver = ChromiumPage(self.opt)
        self.driver.wait(5)
        # self._check_a9tool_urls()
        self.driver.get(self.start_url())
        self.driver.set.activate()

    def open_fingerprint_info_page(self):
        """
        打开指纹测试网站
        """
        self.driver.new_tab("https://web.uutool.cn")

    def _import_fingerprint_info(self, tab) -> None:
        """
        导入指纹信息，如果有旧的，会覆盖旧的，慎重
        """
        if self.input_info.fingerprint:
            logger.info(
                f"exist fingerprint:{self.input_info.fingerprint.model_dump_json()}"
            )
            tab.ele("#fpi").input(self.input_info.fingerprint.model_dump_json())
        else:
            tab.ele("#fpi").input(self.fingerprint.model_dump_json())

        tab.ele("#ibtn").click()

    def load_fingerprint_info(self) -> dict:
        with open(self.fingerprint_info_path, "r") as f:
            data = json.load(f)
        return data

    @staticmethod
    def generate_fingerprint():
        """"""
        # return random_fingerprint()

    def finish(self) -> None:
        self.opt.save(f"{self.input_info.user_data_path}/config.ini")
        with open(self.fingerprint_info_path, "w") as f:
            json.dump(self.fingerprint.model_dump(), f)

    def override_fingerprint(self, fingerprint: FingerprintModel) -> None:
        pass

    def wait_new_tab(self, timeout=10, close_others=True) -> ChromiumTab:
        """
        等待新的 tab 打开
        close_others: 由于钱包的弹窗窗口有时候点击签名以后，会自己关闭，导致框架
            这边未及时释放窗口，导致获取新标签失败，所以等待之前，可关闭除主窗口
            之外的其他标签
        """
        if close_others:
            self.driver.close_tabs(self.driver.tab_id, others=True)
        self.driver.wait(0.2, 0.5)
        while timeout > 0:
            tab = self.driver.wait.new_tab(1)
            if tab:
                logger.error(tab)
                tab = self.driver.get_tab(tab)
                return tab
            timeout -= 1
        raise Exception(f"等待新的 tab 超时 {timeout}s")

    def twitter_login_by_token_tw(
        self, tw_token: str, tab: ChromiumTab | ChromiumPage, after_login_close=True
    ):
        """
        twitter token login
        只处理页面逻辑，不管 tab 逻辑
        tab 的打开与否具体项目中处理
        """
        js = f"""
        document.cookie = 'auth_token={tw_token}; domain=twitter.com; path=/; secure;'
        """
        logger.info(js)
        tab.run_js(js)
        tab.refresh()

    def twitter_login_by_token(self, tw_token: str, tab, after_login_close=False):
        """
        twitter token login
        只处理页面逻辑，不管 tab 逻辑
        tab 的打开与否具体项目中处理
        """
        tab.get("https://x.com")
        tab.wait.load_start()
        url = urlparse(tab.url)
        if url.path == "/home":
            logger.success("already login")
            return True
        utc_datetime = datetime.utcnow()
        exp_date = utc_datetime + timedelta(days=365)
        exp_date = exp_date.strftime("%a, %d %b %Y %H:%M:%S GMT")
        js = f"""
        document.cookie = 'auth_token={tw_token}; domain=x.com; path=/;expires={exp_date}; secure;'
        """
        tab.run_js(js)
        tab.get("https://x.com")
        if after_login_close:
            tab.close()
        return True

    def twitter_click_like(self, tab: ChromiumTab | ChromiumPage):
        """
        点赞推文
        """
        logger.info("点赞推文")
        if self._twitter_click_modal(tab):
            logger.success("like success")
            return
        like_btn = tab.ele("@data-testid=like")
        if like_btn:
            logger.success("like success")
            like_btn.click()
            return
        unlike_btn = tab.ele("@data-testid=unlike")
        if unlike_btn:
            logger.success("already like!")
            return
        logger.error("未找到点赞按钮")

    def _twitter_click_modal(self, tab: ChromiumTab | ChromiumPage) -> bool:
        """
        twitter 任务跳转以后确认弹窗
        点赞、关注任务大多数跳转以后支持弹窗模式的点击
        """
        btn = tab.ele("@data-testid=confirmationSheetConfirm")
        if not btn:
            return False
        btn.click()
        return True

    def twitter_follow_user(self, tab: ChromiumTab | ChromiumPage):
        """
        关注用户
        """
        logger.info("关注用户")
        if self._twitter_click_modal(tab):
            logger.success("modal is follow success")
        url = urlparse(tab.url)
        if "x.com" in url.netloc:
            if "screen_name=" in tab.url:
                screen_name = parse_qs(url.query).get("screen_name", [])
            else:
                screen_name = url.path.replace("/", "")
        elif "twitter.com" in url.netloc:
            screen_name = url.path.replace("/", "")
        else:
            screen_name = None
        if not screen_name:
            logger.error("检查页面是否为用户页面")
            return
        screen_name = screen_name[0]
        follow_user_btn = tab.ele(f"tag:button@@aria-label:@{screen_name}")
        if follow_user_btn:
            test_dataid = str(follow_user_btn.attr("data-testid"))
            if "unfollow" in test_dataid:
                logger.success(f"already follow {screen_name}")
                return
            follow_user_btn.click()
            logger.success(f"follow {screen_name} success")
            return
        logger.error("未找到关注按钮")

    def twitter_retweet(self, tab: ChromiumTab | ChromiumPage):
        """
        转发推文
        """
        logger.info("转发推文")
        if self._twitter_click_modal(tab):
            logger.success("retweet success")
            return
        retweet_btn = tab.ele("@data-testid=retweet")
        if retweet_btn:
            retweet_btn.click()
            retweet_confirm_btn = tab.ele("@data-testid=retweetConfirm")
            if retweet_confirm_btn:
                retweet_confirm_btn.click()
                logger.success("retweet success")
                return
        unretweet_btn = tab.ele("@data-testid=unretweet")
        if unretweet_btn:
            logger.success("already retweet!")
            return
        logger.error("未找到转发按钮")

    def twitter_post_tweet(self, tab: ChromiumTab | ChromiumPage, text: str = ""):
        """
        发布推文
        tweetTextarea_0RichTextInputContainer
        tweetButton
        """
        logger.info("发布推文")
        if text:
            tweet_textarea = tab.ele(
                "@data-testid=tweetTextarea_0RichTextInputContainer"
            )
            if not tweet_textarea:
                logger.error("未找到发布输入框")
                return
            tweet_textarea.input(text)
        tweet_btn = tab.ele("@data-testid=tweetButton")
        if not tweet_btn:
            logger.error("未找到发布按钮")
            return
        tweet_btn.click()
        logger.success("发布推文成功")

    def twitter_tweet_comment(self, tab):
        logger.info("评论推文")
        comment_btn = tab.ele("@data-testid=tweetButton")
        if not comment_btn:
            logger.error("未找到评论按钮")
            return
        comment_btn.click()

    def twitter_auth(self, tab: ChromiumTab | ChromiumPage):
        logger.info("授权")
        auth_btn = tab.ele("tag:button@@data-testid=OAuth_Consent_Button")
        if auth_btn:
            auth_btn.click()
        else:
            auth_btn = tab.ele("tag:input@@id=allow")
            if auth_btn:
                auth_btn.click()
        logger.error("未找到授权按钮")

    def dc_login_by_token(
        self, dc_token: str, tab: ChromiumTab | ChromiumPage, after_login_close=True
    ):
        """
        dc token login
        只处理页面逻辑，不管 tab 逻辑
        tab 的打开与否具体项目中处理
        """
        tab.get("https://discord.com/login")
        if tab.wait.url_change("https://discord.com/channels/@me", timeout=10):
            logger.success("already login")
            return
        js = f"""
            window.t = "{dc_token}";
            window.localStorage = document.body.appendChild(document.createElement `iframe`).contentWindow.localStorage;
            window.setInterval(() => window.localStorage.token=`"${{window.t}}"`);
            window.location.reload();
            """
        tab.run_js(js)
        tab.get("https://discord.com/channels/@me")

    def add_metamask_extension(self):
        abspath = os.path.join(os.path.pardir, "metamask")
        metamask_path = os.path.abspath(abspath)
        if not os.path.exists(metamask_path):
            raise Exception(
                f"钱包插件目录未找到，请确认插件在以下位置\n{metamask_path}"
            )
        if "extensions/metamask" in self.opt.extensions:
            self.opt.extensions.remove("extensions/metamask")
        self.add_extension(metamask_path)

    def login_by_2fa(self):
        logger.debug("通过 2fa 进行登录 ")
        if not self.input_info.twitter:
            raise Exception("未配置 2fa 登录的配置 ")
        self.driver.get(self.start_url())
        if urlparse(self.driver.url).path == "/home":
            logger.success("已经登录状态 ")
            return True
        sign_btn = self.driver.ele("tag:a@@data-testid=loginButton")
        if not sign_btn:
            raise Exception("未找到登录按钮 ")
        sign_btn.click()
        self.driver.wait.load_start()
        username_input = self.driver.ele("tag:input@@autocomplete=username")
        if not username_input:
            raise Exception("未找到登录按钮 ")
        logger.debug("input username")
        username_input.input(self.input_info.twitter.username)
        next_btn = self.driver.ele("tag:span@@text()=Next")
        if not next_btn:
            raise Exception("未找到 Next 按钮 ")
        next_btn.click()
        self.driver.wait.load_start()
        pwd_input = self.driver.ele("tag:input@@autocomplete=current-password")
        if not pwd_input:
            raise Exception("未找到密码输入框 ")
        pwd_input.input(self.input_info.twitter.password)
        login_btn = self.driver.ele("tag:button@@data-testid=LoginForm_Login_Button")
        if not login_btn:
            raise Exception("未找到登录按钮 ")
        login_btn.click()
        p2fa_input = self.driver.ele("tag:input@@data-testid=ocfEnterTextTextInput")
        if p2fa_input:
            code = get_2fa_code(self.input_info.twitter.p2fa)
            if not code:
                raise Exception("未获取到 2fa 验证码")
            logger.success(f"输入 2fa 验证码 {code}")
            p2fa_input.input(code)
            btn = self.driver.ele("tag:button@@data-testid=ocfEnterTextNextButton")
            if not btn:
                raise Exception("未找到 Next 按钮 ")
            btn.click()
            logger.success("success")
            logger.success(f"{self.driver.cookies(as_dict=True)}")
            self.driver.wait.load_start()

    def check_bot(self, driver, time_out=5):
        """cf校验"""
        logger.info("check_bot ...")
        while time_out > 0:
            try:
                logger.info(f"check_bot time_out:{time_out}")
                time_out -= 1
                driver.wait(1)
                tab = self.driver.get_tab(title="Just a moment...")
                if not tab:
                    logger.info("not found cf verify")
                    return
                cf_iframe = driver.get_frame(1)
                if cf_iframe.states.ready_state == "complete":
                    if driver.title != "Just a moment...":
                        logger.info("is not cf checkpage")
                        return
                    checkbox = cf_iframe.ele("tag:input@type=checkbox")
                    if checkbox:
                        checkbox.click()
                        driver.wait.load_start()
                    return
            except Exception as e:
                logger.error(e)
        raise Exception("check_bot error")
