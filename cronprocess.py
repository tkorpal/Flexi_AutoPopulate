import os
import sys
import pyodbc
from queries import flexi_uploads
from process1_flexicapture import flexicapture_uploads, flexicapture_assetmark, errors_transactions

'''
-- Rayond James 7B5F4757-CB22-E211-969B-782BCB14085F
-- UMB 93D0C0F1-80AF-DD11-907E-001AA0C8FB71
-- BOK 0E8F3927-258D-E311-ACA0-782BCB14085F
-- Fifth Third 0AD0C0F1-80AF-DD11-907E-001AA0C8FB71
-- Truist CBEF69F2-379F-EC11-B842-0050569CCC36
-- US Bank 98D0C0F1-80AF-DD11-907E-001AA0C8FB71
-- AssetMark E11899D9-EFEB-DD11-924D-00221912ADEF
'''    

years = ('2022',)
months = ('01','02','03','04','05','06','07','08','09','10','11','12',)
# months = ('01',)
# years = ('2022',)


bankfolders = {
    '0AD0C0F1-80AF-DD11-907E-001AA0C8FB71' : 'Fifth Third Bank',
    '0E8F3927-258D-E311-ACA0-782BCB14085F' : 'BOK Financial -Bank of Oklahoma Financial',
    # 'E11899D9-EFEB-DD11-924D-00221912ADEF' : 'AssetMark',
}


if __name__ == '__main__':
    # upload_to_autopopulate()
    # processed_schedule_d()
    # errors_transactions()
    banks_ready = flexi_uploads()
    for x in banks_ready:
        folder = f'/home/ubuntu/Clients/Custodial_Bank Statements/{bankfolders[x[0]]}/Banking'
        for year in years:
            for month in months:
                source = f"{folder}/{year}/{month}"
                print(f"{bankfolders[x[0]]} {month} {year}")
                if bankfolders[x[0]] == 'AssetMark':
                    pass
                    # flexicapture_assetmark(bankfolders[x[0]], source, month, year)
                else:                                         
                    flexicapture_uploads(bankfolders[x[0]], source, month, year)