import atexit
from pyVim.connect import SmartConnectNoSSL, Disconnect
from pyVmomi import vim
import app
import util
import export_csv

def print_vminfo(vm, dns, owner, depth=1):
    if hasattr(vm, 'childEntity'):
        if depth > 10:
            return None

        vmlist = vm.childEntity

        for child in vmlist:
            print_vminfo(child, depth+1)

        return None

    summary = vm.summary

    nam = None
    dict_vals = {"Name": None, "State": None, "Status": None, "OS": None, "ManagedBy": None, "IPAddress": None, "Owner": None, "DNS": None}

    if hasattr(summary.config, "name") is False:
        return

    if owner is None:
        dict_vals["Owner"] = "[NoValue]"

    if dns is None:
        dict_vals["DNS"] = "[NoValue]"

    # print("Name:: " + summary.config.name)
    dict_vals["Name"] = summary.config.name

    # print("State:: " + summary.runtime.powerState)
    dict_vals["State"] = summary.runtime.powerState

    # print("Status:: " + summary.guest.toolsStatus)
    dict_vals["Status"] = summary.guest.toolsStatus

    # print("OS:: " + summary.config.guestFullName)
    dict_vals["OS"] = summary.config.guestFullName

    if summary.config.managedBy is None:
        managed = "[NoValue]"

    else:
        managed = summary.config.managedBy

    # print("Managed By:: " + managed)
    dict_vals["ManagedBy"] = managed

    # print("Hostname:: " + summary.config.network.dnsConfig.hostName)

    if summary.guest.ipAddress is not None:
        ip_addr = summary.guest.ipAddress
    else:
        ip_addr = "[NoValue]"

        print("IP Address:: " + ip_addr)
        dict_vals["IPAddress"] = ip_addr

    # print("\n")
    return dict_vals


def listear():
    dns_hostname = None
    owner = None
    vms_vector = []

    a = app.App()
    utils = util.Util()
    config = a.get_creds("config.json")
    ip = config["ip"]
    usr = utils.b64_decrypt(config["usr"])
    pwd = utils.b64_decrypt(config["passwd"])

    si = SmartConnectNoSSL(host=ip, user=usr, pwd=pwd)

    atexit.register(Disconnect, si)
    content = si.RetrieveContent()
    cfm = content.customFieldsManager

    if cfm is None:
        print("[!] OWNER not available")

    else:
        required_field = ["Owner"]
        my_customField = {}
        for my_field in cfm.field:
            if my_field.name in required_field:
                my_customField[my_field.key] = my_field.name
                # print("Owner:: " + my_field.name)
                owner = my_field.name

    cv = content.viewManager.CreateContainerView(
        container=content.rootFolder, type=[vim.HostSystem], recursive=True)

    for child in cv.view:
        dns_hostname = child.config.network.dnsConfig.hostName
        # print("DNS Name:: ", dns_hostname)


    for datacenter in content.rootFolder.childEntity:
        # print("datacenter : " + datacenter.name)
        vmFolder = datacenter.vmFolder
        vmlist = vmFolder.childEntity

        for vm in vmlist:
            vms_dict = print_vminfo(vm, dns_hostname, owner)

            if vms_dict is not None:
                vms_vector.append(vms_dict)

    return vms_vector


dats_vector = listear()
class_csv = export_csv.ToCsv()
headers = ["Name", "State", "Status", "OS", "ManagedBy", "IPAddress", "Owner", "DNS"]
class_csv.export_csv("esix_vms.csv", headers, dats_vector)