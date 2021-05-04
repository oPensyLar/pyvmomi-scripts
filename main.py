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
    print("Name:: " + summary.config.name)
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

    ip = "192.168.1.149"
    creds_b64 = a.get_creds("creds.json")
    usr = utils.b64_decrypt(creds_b64["usr"])
    pwd = utils.b64_decrypt(creds_b64["passwd"])

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