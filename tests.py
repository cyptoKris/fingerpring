from DrissionPage import ChromiumPage, ChromiumOptions

opt = ChromiumOptions()
opt.set_local_port(9222)


driver = ChromiumPage(opt)
btn = driver.ele("@data-testid=confirmationSheetConfirm")
print(btn)
