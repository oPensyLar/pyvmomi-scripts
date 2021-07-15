import atexit
from pyVim.connect import SmartConnectNoSSL, Disconnect
from pyVmomi import vim
import app
import util
import export_csv
import socket
from datetime import datetime, timezone


intervals = (
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hours', 3600),    # 60 * 60
    ('minutes', 60),
    ('seconds', 1),
    )


def display_time(seconds, granularity=2):
    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result[:granularity])


def get_config():
    a = app.App()
    utils = util.Util()
    config = a.get_creds("config.json")
    ip = config["ip"]
    esxi_dns_hostname = dns_resolver(ip)
    usr = utils.b64_decrypt(config["usr"])
    pwd = utils.b64_decrypt(config["passwd"])

    return {"server_ip":  ip, "server_dns_name": esxi_dns_hostname, "user_name": usr, "user_password": pwd}


def dns_resolver(ip_addr):
    try:
        dns_nam = socket.gethostbyaddr(ip_addr)
        dns_nam = dns_nam[0]

    except socket.herror:
        dns_nam = "Unknow"

    return dns_nam


def print_vminfo(vm, cluster, server_dats, depth=1):
    if hasattr(vm, 'childEntity'):
        if depth > 10:
            print("depth > 10")
            return None

        vmlist = vm.childEntity

        for child in vmlist:
            print_vminfo(child, cluster, server_dats, depth+1)

        return None

    summary = vm.summary

    nam = None

    if hasattr(vm.runtime, "bootTime") is False or vm.runtime.bootTime is None:
        t = "[NoValue]"

    else:
        now = datetime.now(timezone.utc)
        delta = now - vm.runtime.bootTime
        t = display_time(delta.total_seconds())

    dict_vals = {"name": None,
                 "state": None,
                 "status": vm.configStatus,
                 "cluster": cluster.name,
                 "boot_time": t,
                 "os": None,
                 "managed_by": vm.config.managedBy,
                 "vm_ip_address": None,
                 "vm_dns_name": None,
                 "owner": None,
                 "esxi_ip_address_server": server_dats["server_ip"],
                 "esxi_dns_name_server": server_dats["server_dns_name"]}

    if dict_vals["status"] == "green":
        dict_vals["status"] = "Normal"

    if hasattr(vm, "guest") is False:
        dict_vals["vm_ip_address"] = "[NoValue]"
        dict_vals["vm_dns_name"] = dict_vals["vm_ip_address"]

    else:
        nets = vm.guest.net

        for net in nets:
            for c_ipAddress in net.ipAddress:
                dict_vals["vm_ip_address"] = c_ipAddress
                dict_vals["vm_dns_name"] = dns_resolver(dict_vals["vm_ip_address"])

    if hasattr(summary.config, "name") is False:
        return

    # "server_ip": ip, "server_dns_name": esxi_dns_hostname,
    dict_vals["owner"] = "[NoValue]"

    # print("Name:: " + summary.config.name)
    dict_vals["name"] = summary.config.name

    dict_vals["state"] = summary.runtime.powerState

    dict_vals["os"] = summary.config.guestFullName

    return dict_vals


def listear(cfg_dats):
    owner = None
    cluster = None
    vms_vector = []

    si = SmartConnectNoSSL(host=cfg_dats["server_ip"],
                           user=cfg_dats["user_name"],
                           pwd=cfg_dats["user_password"])

    # atexit.register(Disconnect, si)
    content = si.RetrieveContent()
    # cfm = content.customFieldsManager
    # cv = content.viewManager.CreateContainerView(container=content.rootFolder, type=[vim.HostSystem], recursive=True)

    obj_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                       [vim.StoragePod],
                                                       True)
    ds_cluster_list = obj_view.view
    obj_view.Destroy()

    for ds_cluster in ds_cluster_list:
        datastores = ds_cluster.childEntity
        print("Datastores: ")

        for datastore in datastores:
            print(datastore.name)

    for datacenter in content.rootFolder.childEntity:
        print("datacenter : " + datacenter.name)
        vmFolder = datacenter.vmFolder
        vmlist = vmFolder.childEntity

        clusters = datacenter.hostFolder.childEntity

        for c_cluster in clusters:
            cluster = c_cluster

        for vm in vmlist:
            # cfg_dats
            vms_dict = print_vminfo(vm, cluster, cfg_dats)

            if vms_dict is not None:
                vms_vector.append(vms_dict)

    return vms_vector


config_dats = get_config()
dats_vector = listear(config_dats)

class_csv = export_csv.ToCsv()

headers = ["name",
           "state",
           "status",
           "cluster",
           "boot_time",
           "os",
           "managed_by",
           "vm_ip_address",
           "vm_dns_name",
           "owner",
           "esxi_ip_address_server",
           "esxi_dns_name_server"]

class_csv.export_csv("esix_vms.csv", headers, dats_vector)