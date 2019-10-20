from ftplib import FTP


def download_people_data(file_path):

    url = "ftp://ftp.worldpop.org.uk/GIS/Population/Global_2000_2020/2019/0_Mosaicked/ppp_2019_1km_Aggregated.tif"

    with FTP("ftp.worldpop.org.uk") as ftp:
        ftp.login()
        ftp.cwd("GIS/Population/Global_2000_2020/2019/0_Mosaicked")

        with open(file_path, "wb") as fp:
            ftp.retrbinary("RETR ppp_2019_1km_Aggregated.tif", fp.write)
