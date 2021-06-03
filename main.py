import atexit
from pyVim.connect import SmartConnectNoSSL, Disconnect
from pyVmomi import vim
import app
import util
import export_csv
import socket


def dns_resolver(ip_addr):
    try:
        dns_nam = socket.gethostbyaddr(ip_addr)
        dns_nam = dns_nam[0]

    except socket.herror:
        dns_nam = "Unknow"

    return dns_nam


def print_vminfo(esix_ip_address, vm, dns, owner, depth=1):
    if hasattr(vm, 'childEntity'):
        if depth > 10:
            return None

        vmlist = vm.childEntity

        for child in vmlist:
            print_vminfo(esix_ip_address, child, owner, depth+1)

        return None

    summary = vm.summary
    nets = vm.guest.net

    nam = None
    dict_vals = {"name": None, "state": None, "status": None, "os": None, "managed_by": None, "vm_ip_address": None, "vm_dns_name": None, "owner": None, "esxi_ip_address_server": None, "dns_server": None}

    for net in nets:
        for c_ipAddress in net.ipAddress:
            dict_vals["vm_ip_address"] = c_ipAddress

    if hasattr(summary.config, "name") is False:
        return

    if owner is None:
        dict_vals["owner"] = "[NoValue]"

    if dns is None:
        dict_vals["dns_name"] = "[NoValue]"

    # print("Name:: " + summary.config.name)
    dict_vals["name"] = summary.config.name

    # print("State:: " + summary.runtime.powerState)
    dict_vals["state"] = summary.runtime.powerState

    # print("Status:: " + summary.guest.toolsStatus)
    dict_vals["status"] = summary.guest.toolsStatus

    # print("OS:: " + summary.config.guestFullName)
    dict_vals["os"] = summary.config.guestFullName

    if summary.config.managedBy is None:
        managed = "[NoValue]"

    else:
        managed = summary.config.managedBy

    # print("Managed By:: " + managed)
    dict_vals["managed_by"] = managed

    # print("\n")
    return dict_vals


def listear():
    esxi_dns_hostname = None
    owner = None
    vms_vector = []

    a = app.App()
    utils = util.Util()
    config = a.get_creds("config.json.test")
    ip = config["ip"]
    esxi_dns_hostname = dns_resolver(ip)
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


    for datacenter in content.rootFolder.childEntity:
        # print("datacenter : " + datacenter.name)
        vmFolder = datacenter.vmFolder
        vmlist = vmFolder.childEntity

        for vm in vmlist:
            vms_dict = print_vminfo(ip, vm, esxi_dns_hostname, owner)

            if vms_dict is not None:
                vms_vector.append(vms_dict)

    return vms_vector


dats_vector = listear()
class_csv = export_csv.ToCsv()
headers = ["name", "state", "status", "os", "managed_by", "vm_ip_address", "vm_dns_name", "owner", "esxi_ip_address_server", "dns_server"]
class_csv.export_csv("esix_vms.csv", headers, dats_vector)