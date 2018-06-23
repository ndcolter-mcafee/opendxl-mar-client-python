MAR_SEARCHID = "ipaddrid"

MAR_HOST_IP_ADDRESS_1 = "192.168.130.152"

MAR_HOST_IP_ADDRESS_2 = "192.168.130.133"

MAR_DIRECT_INVOKE_SEARCH_POST = {
    "body": {
        "projections": [
            {
                "name": "HostInfo",
                "outputs": [
                    "ip_address"
                ]
            }
        ]
    },
    "method": "POST",
    "parameters": {},
    "target": "/v1/simple"
}

MAR_PROCESS_IDS = [
    "MARService.exe",
    "OneDrive.exe",
    "RuntimeBroker.exe",
    "SearchIndexer.exe",
    "SearchUI.exe",
    "ShellExperienceHost.exe",
    "SkypeHost.exe",
    "System",
    "UpdaterUI.exe",
    "VGAuthService.exe",
    "WUDFHost.exe",
    "WmiApSrv.exe",
    "WmiPrvSE.exe",
    "WmiPrvSE.exe",
    "[System Process]"
]
