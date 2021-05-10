import atexit
from pyVim.connect import SmartConnectNoSSL, Disconnect
from pyVmomi import vim
import app
import util


def print_vminfo(vm, depth=1):
    if hasattr(vm, 'childEntity'):
        if depth > 10:
            return

        vmlist = vm.childEntity

        for child in vmlist:
            print_vminfo(child, depth+1)

        return

    summary = vm.summary

    nam = None

    if hasattr(summary.config, "name"):
        nam = summary.config.name

    else:
        nam = "[NoName]"

    print("Name:: " + nam)
    print("PowerState:: " + summary.runtime.powerState)
    print("Guest:: " + summary.config.guestFullName)
    # print("Hostname:: " + summary.config.network.dnsConfig.hostName)

    if summary.guest.ipAddress is not None:
        print("IP Address:: " + summary.guest.ipAddress)
    else:
        print("IP Address:: None")

    print("\n")


def listear():
    a = app.App()
    utils = util.Util()

    config = a.get_creds("config.json")
    ip = config["ip"]
    usr = utils.b64_decrypt(config["usr"])
    pwd = utils.b64_decrypt(config["passwd"])

    si = SmartConnectNoSSL(host=ip, user=usr, pwd=pwd)

    atexit.register(Disconnect, si)
    content = si.RetrieveContent()

    cv = content.viewManager.CreateContainerView(
        container=content.rootFolder, type=[vim.HostSystem], recursive=True)

    for child in cv.view:
        print(child.name, "== ", child.config.network.dnsConfig.hostName)

    for datacenter in content.rootFolder.childEntity:
        print("datacenter : " + datacenter.name)
        vmFolder = datacenter.vmFolder
        vmlist = vmFolder.childEntity

        for vm in vmlist:
            print_vminfo(vm)


listear()