import os
from config.settings import settings

def load_proxy(plugin_path: str) -> None:
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 3,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "webRequest",
            "webRequestBlocking",
            "webRequestAuthProvider"
        ],
        "host_permissions": [
            "<all_urls>"
        ],
        "background": {
            "service_worker": "background.js"
        },
        "minimum_chrome_version": "88"
    }
    """

    background_js = """
    var config = {
        mode: "fixed_servers",
        rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
            },
            bypassList: ["localhost"]
        }
    };

    chrome.proxy.settings.set({value: config, scope: "regular"}, () => {});

    chrome.webRequest.onAuthRequired.addListener(
        (details) => ({
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        }),
        { urls: ["<all_urls>"] },
        ["blocking"]
    );
    """ % (settings.proxy.proxy_host, settings.proxy.proxy_port, settings.proxy.proxy_user, settings.proxy.proxy_pass)
    
    plugin_path = plugin_path + '/proxy_ext'
    os.makedirs(plugin_path, exist_ok=True)
    with open(os.path.join(plugin_path, "manifest.json"), "w") as manifest_file:
        manifest_file.write(manifest_json)
    with open(os.path.join(plugin_path, "background.js"), "w") as background_file:
        background_file.write(background_js)
    return plugin_path
