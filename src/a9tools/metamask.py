import os
from urllib.parse import urlparse
from time import sleep
from .exception import WalletInfoException
from .log import logger
from .utils import log_execution_time
from .model import WalletInfo


class MetaMaskException(WalletInfoException):
    def __init__(self, info: str):
        super().__init__("MetaMask")
        self.info = info

    def __repr__(self):
        return f"{self.name} Acitons Error: {self.info}"


class MetaMask:
    def get_url(self):
        """
        获取插件的本地地址
        用于处理 extension_id 在不同机器,不同版本上不同的问题
        """
        return self.get_extension_url()

    def __click_by_data_testid(self, dt_id, tab):
        """
        统一点击按钮
        """
        ele = tab.ele(f"@data-testid={dt_id}")
        if ele:
            ele.click()
        else:
            logger.debug(f"{dt_id} not found")

    def click_actions(self, dt_ids: list, tab):
        """
        任务链的方式点击
        dt_ids: 有序的 data_testid 列表
        """
        logger.info("click create wallet btn..")
        for act in dt_ids:
            self.__click_by_data_testid(act, tab)

    def setup(self, create_tag: bool, pk: str, tab):
        """
        初始化钱包
        可选使用
        """
        self.init_wallet_extension(tab)
        if create_tag:
            self.create_extension_pwd(tab)
            self.into_home_page(tab)
            self.import_wallet(pk, tab)
            tab.close()

    def init_wallet_extension(self, tab) -> None:
        """
        跳过协议，创建钱包，点击我同意
        """
        logger.info(f"{tab.title}\n跳过协议，创建钱包，点击我同意")
        actions = [
            "onboarding-terms-checkbox",
            "onboarding-create-wallet",
            "metametrics-i-agree",
        ]
        self.click_actions(actions, tab)

    def create_extension_pwd(self, tab, password: str = "localpwd"):
        """
        输入钱包插件解锁密码
        """
        logger.info("创建钱包插件解锁密码")
        tab.ele("@data-testid=create-password-new").input(password)
        tab.ele("@data-testid=create-password-confirm").input(password)
        actions = [
            "create-password-terms",
            # "create-password-wallet"
        ]
        self.click_actions(actions, tab)
        createBtn = tab.ele("tag:button@@data-testid=create-password-wallet")
        if createBtn:
            createBtn.click()
            return
        import_btn = tab.ele("@text()=Import my wallet")
        if import_btn:
            import_btn.click()
            return

    def into_home_page(self, tab, wallet: WalletInfo = {}) -> None:
        """
        当有本地数据的时候，进入钱包首页
        """
        logger.info("进入钱包插件首页")
        # 判断是否有解锁按钮
        input_box = tab.ele("@data-testid=unlock-password")
        if input_box:
            self.unlock_wallet(tab, wallet=wallet)
            return
        self._into_home_page(tab)

    def _into_home_page(self, tab) -> None:
        """
        第一次进入首页
        """
        # 如果没有解锁按钮，直接进入创建钱包逻辑
        actions = [
            "secure-wallet-later",
            "skip-srp-backup-popover-checkbox",
            "skip-srp-backup",
            "onboarding-complete-done",
            "pin-extension-next",
            "pin-extension-done",
        ]
        self.click_actions(actions, tab)

        section = tab.ele("tag:section")
        if not section:
            logger.error("未找到 section")
            return
        logger.info(f"section: {section}")
        enable_btn = section.ele("tag:button@@text():Enable")
        if enable_btn:
            logger.info(f"enable_btn: {enable_btn}")
            enable_btn.click(by_js=True)
        while True:
            section = tab.ele("tag:section")
            if not section:
                logger.error("未找到 section")
                break
            close_btn = section.ele("tag:button@@data-testid=popover-close")
            if close_btn:
                logger.info(f"close_btn: {close_btn}")
                close_btn.click(by_js=True)
            else:
                break
        btn = tab.ele("@text()=Got it")
        if btn:
            btn.click()

    def import_wallet(self, pk: str, tab) -> None:
        """
        导入钱包
        """
        # tab.get(self.get_extension_url())
        logger.info(f"refresh url: {tab.url}")
        logger.info("导入钱包")
        self.__click_by_data_testid("account-menu-icon", tab)
        self.__click_by_data_testid(
            "multichain-account-menu-popover-action-button", tab
        )
        section = tab.ele("tag:section")
        div = section.ele("@class=mm-box mm-box--padding-4")
        divs = div.eles("tag:div")
        divs[1].ele("tag:button").click()
        tab.ele("@id=private-key-box").input(pk)
        self.__click_by_data_testid("import-account-confirm-button", tab)
        tab.close()

    def import_wallet_mnemonic(self, mnemonic: str, tab) -> None:
        """
        导入助记词
        """
        act = [
            "onboarding-terms-checkbox",
            "onboarding-import-wallet",
            "metametrics-i-agree",
        ]
        self.click_actions(act, tab)
        mnemonic_list = mnemonic.split(" ")
        if len(mnemonic_list) != 12:
            raise MetaMaskException("助记词长度不对")
        for i in range(12):
            tab.ele(f"@data-testid=import-srp__srp-word-{i}").input(mnemonic_list[i])
        tab.ele("@data-testid=import-srp-confirm").click()

    def import_wallet_git_version(self, pk: str, tab) -> None:
        """
        旧版小狐狸插件导入钱包
        """
        tab.get(self.get_extension_url())
        tab.wait.load_start()
        tab.get(self._get_import_wallet_url())
        logger.info(f"refresh url: {tab.url}")
        tab.ele("@id=private-key-box").input(pk)
        tab.ele("@text()=Import").click()
        tab.close()

    @log_execution_time
    def unlock_wallet(
        self, tab, with_close: bool = True, wallet: WalletInfo = {}
    ) -> None:
        """
        解锁插件
        with_close: 是否关闭 tab
        """
        logger.info("解锁插件")
        tab.ele("@data-testid=unlock-password").input("localpwd")
        tab.ele("@data-testid=unlock-submit").click()
        if tab.wait.ele_displayed(
            "tag:button@@data-testid=onboarding-complete-done", timeout=3
        ):
            tab.ele("tag:button@@data-testid=onboarding-complete-done").click()
            tab.wait.eles_loaded("tag:button@@data-testid=pin-extension-next")
            tab.ele("tag:button@@data-testid=pin-extension-next").click()
            tab.wait.eles_loaded("tag:button@@data-testid=pin-extension-done")
            tab.ele("tag:button@@data-testid=pin-extension-done").click()
        close_btn = tab.ele("tag:button@@data-testid=popover-close")
        if close_btn:
            close_btn.click(by_js=True)
        
        if with_close:
            gotItBtn = tab.ele("tag:button@@text()=Got it")
            if gotItBtn:
                gotItBtn.click()
            hasSpan = tab.ele("tag:span@@text()=Account 1")
            if hasSpan and wallet:
                logger.info("need import private key")
                if not wallet.mnemonic:
                    self.import_wallet(wallet.private_key, tab=tab)
                    return
        tab.ele("tag:button@@data-testid=network-display").click()
        tab.wait(1)
        tab.ele("tag:div@@data-testid=Ethereum Mainnet").click()
        tab.wait(3)
        tab.close()

    def click_next(self, tab) -> None:
        """
        下一步
        """
        logger.info("点击下一步")
        btn = tab.ele("@data-testid=page-container-footer-next")
        if btn:
            logger.debug("click by data-testid")
            btn.click()
            return
        old_version_next_btn = tab.ele("tag:button@text():Next")
        if old_version_next_btn:
            logger.debug("click by text")
            old_version_next_btn.click()
            return
        logger.error("next btn not found")

    def click_confirm(self, tab):
        """
        点击确认
        """
        logger.info("点击确认")
        self.click_next(tab)

    def click_sign(self, tab) -> None:
        """
        签名
        """
        logger.info("点击签名")
        self.click_next(tab)

    def click_approve(self, tab) -> None:
        """
        批准
        """
        logger.info("点击批准")
        btn = tab.ele("@data-testid=confirmation-submit-button")
        if btn.wait.enabled():
            btn.click()

    def save_extension_url(self, tab) -> None:
        """
        保存扩展程序本机的 地址
        """
        self.save_extension_id(tab)
        with open(f"{self.__class__.__name__}.url", "w") as f:
            f.write(tab.url)

    def get_extension_url(self) -> str:
        """
        获取本机的 url
        """
        id_path = f"{self.__class__.__name__}.id"
        if os.path.exists(id_path):
            with open(id_path, "r") as f:
                _id = f.read()
                return f"chrome-extension://{_id}/home.html"
        with open(f"{self.__class__.__name__}.url", "r") as f:
            return f.read()

    def save_extension_id(self, tab) -> None:
        """
        保存扩展程序的 id
        """
        parse_url = urlparse(tab.url)
        with open(f"{self.__class__.__name__}.id", "w") as f:
            f.write(parse_url.netloc)

    def _get_import_wallet_url(self) -> str:
        id_path = f"{self.__class__.__name__}.id"
        if os.path.exists(id_path):
            with open(id_path, "r") as f:
                _id = f.read()
                return f"chrome-extension://{_id}/home.html#new-account/import"
        raise MetaMaskException(f"{self.__class__.__name__}.id not found")
