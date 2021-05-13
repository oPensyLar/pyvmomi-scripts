import csv


class ToCsv:
    @staticmethod
    def export_csv(fich, fieldnames, data):

        with open(fich, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)




        # with open(fich, 'w') as csvfile:
            # writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # writer.writeheader()
            # writer.writerow({'Grade': 'B', 'first_name': 'Alex', 'last_name': 'Brian'})
            # writer.writerow({'Grade': 'A', 'first_name': 'Rachael',
            #                  'last_name': 'Rodriguez'})
            # writer.writerow({'Grade': 'B', 'first_name': 'Jane', 'last_name': 'Oscar'})
            # writer.writerow({'Grade': 'B', 'first_name': 'Jane', 'last_name': 'Loive'})

        # print("Writing complete")