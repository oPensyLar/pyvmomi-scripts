import json


class App:

    def get_creds(self, file_path):
        with open(file_path) as fp:
            json_data = json.load(fp)

            for key in json_data["creds"]:
                return {"usr": json_data["creds"]["user"],
                        "passwd": json_data["creds"]["password"],
                        "ip": json_data["ip"]}

    def get_array_cmd(self, file_path, sudo_pass):
        array_ret = []

        with open(file_path) as fp:
            json_data = json.load(fp)

            for vals in json_data["cmds"]:
                exists = "sudo" in json_data["cmds"][vals]
                cmd_dict = {"cmd": json_data["cmds"][vals]["cmd"], "sudo": exists}

                if cmd_dict["sudo"]:
                    cmd_one = 'echo ' + sudo_pass + ' | sudo -S ' + cmd_dict["cmd"]
                else:
                    cmd_one = cmd_dict["cmd"]

                array_ret.append(cmd_one)

            return array_ret

