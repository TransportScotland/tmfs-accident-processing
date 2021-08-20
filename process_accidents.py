import sys
from datetime import datetime
import logging

from simpledbf import Dbf5
import pandas as pd
import numpy as np


def miles_to_km(val):
    return val * 1.6


def adjust_beta_factor(beta, year):
    if year <= 2010:
        return beta ** (year - 2000)
    elif 2011 <= year <= 2020:
        return (beta ** (2010 - 2000)
                * ((1 + beta) / 2) ** (year - 2010))
    elif 2021 <= year <= 2030:
        return (beta ** (2010 - 2000)
                * ((1 + beta) / 2) ** (2020 - 2010)
                * ((3 + beta) / 4) ** (year - 2020))
    elif year > 2030:
        return (beta ** (2010 - 2000)
                * ((1 + beta) / 2) ** (2020 - 2010)
                * ((3 + beta) / 4) ** (2030 - 2020))


class AccidentData:
    def __init__(self, network_dbf, year):
        self.df = Dbf5(network_dbf).to_dataframe()
        self.df = self.df[['A', 'B', 'SPEED', 'DISTANCE', 'LINK_CLASS', 'ANN_V']]
        self.year = year

    def get_accident_numbers(self, rates_workbook):
        rates_dict = pd.read_excel(rates_workbook, sheet_name=None, skiprows=1)
        self.df = self.df.merge(rates_dict['A9 links'], how='left')\
                         .merge(rates_dict['Link Class Correspondence'],
                                how='left', left_on='LINK_CLASS',
                                right_on='TMfS Link Class')\
                         .fillna(0)

        self.df = self.df[self.df['Accident Type'] > 0]

        self.df['mvkm'] = self.df['DISTANCE'] * self.df['ANN_V'] / 1000000

        motorway = (self.df['Accident Type'].isin((1, 2, 3)))
        rural = (self.df['SPEED'] > miles_to_km(40))
        urban = (self.df['SPEED'] <= miles_to_km(40))
        # When multiple conditions are satisfied, the first one
        # encountered in condlist is used.
        self.df['Road Type'] = np.select([motorway, rural, urban],
                                         ['Motorway', 'Rural', 'Urban'])

        self.df = self.df.merge(rates_dict['Local Rates Usage'], how='left')\
                         .merge(rates_dict['Accident Rates'], how='left')

        self.df['Beta (adj)'] = self.df['Beta'].apply(
            adjust_beta_factor, year=self.year
        )

        # Single OR DUAL on the dualling section get the ASC modifier at present
        factor_links = ((self.df['Indicator'] > 0)
                        & (self.df['Dualling Section Flag'] == 1))
        self.df['Factor to Apply'] = np.where(
            factor_links, self.df['ASC Factor'], 1
        )
        self.df['No. Accidents'] = (
                self.df['mvkm']
                * self.df['Pia/mvkm']
                * self.df['Beta (adj)']
                * self.df['Factor to Apply']
        )

        self.df = self.df.merge(rates_dict['Casualty Rates'], how='left')\
                         .merge(rates_dict['Casualty Beta Factors'],
                                on=['Accident Type', 'Road Type', 'Rate Type'],
                                suffixes=('', '_CasBeta'), how='left')\
                         .merge(rates_dict['Accident Proportions'],
                                on=['Accident Type', 'Road Type', 'Rate Type'],
                                suffixes=('_CasRate', '_AccProp'), how='left')

        for acc_type in ('Fatal', 'Serious', 'Slight'):
            # Casualty beta factors only apply up to 2010
            self.df[acc_type + '_CasBetaAdj'] = (
                    self.df[acc_type + '_CasBeta'] ** min(self.year-2000, 10)
            )
            self.df[acc_type + ' Casualties'] = (
                    self.df['No. Accidents']
                    * self.df[acc_type + '_CasRate']
                    * self.df[acc_type + '_CasBetaAdj']
            )

            if acc_type != 'Slight':
                self.df[acc_type + '_AccPropAdj'] = (
                        self.df[acc_type + '_AccProp'] * self.df['Beta (adj)']
                )
            else:
                self.df[acc_type + '_AccPropAdj'] = (
                        1 - (self.df['Fatal_AccPropAdj']
                             + self.df['Serious_AccPropAdj'])
                )

            self.df[acc_type + ' Accidents'] = (
                    self.df[acc_type + '_AccPropAdj'] * self.df['No. Accidents']
            )
        # self.df.to_csv('all link temp.csv')

    def export_totals(self, output_name):
        # print(self.df.columns)
        totals = self.df.groupby('Road Type', as_index=False)\
                     .agg({'{} {}'.format(at, mes): 'sum'
                           for mes in ('Casualties', 'Accidents')
                           for at in ('Fatal', 'Serious', 'Slight')})
        # ].sum().to_frame(name='Total')
        
        totals = totals[['Road Type'] + ['{} {}'.format(at, mes) for mes in ('Casualties', 'Accidents') for at in ('Fatal', 'Serious', 'Slight')]]
        
        totals = totals.append(totals.sum(numeric_only=True), ignore_index=True)

        totals['Road Type'] = totals['Road Type'].fillna('Total')

        totals.to_csv(output_name, index=False)


if __name__ == '__main__':
    logging.basicConfig(filename=sys.argv[-2], level=logging.DEBUG)
    try:
        logging.info('Network: ' + sys.argv[1])
        logging.info('Rates Book: ' + sys.argv[2])
        logging.info('Year: ' + sys.argv[3])
        ad = AccidentData(sys.argv[1], year=int(sys.argv[3]))
        ad.get_accident_numbers(rates_workbook=sys.argv[2])
        ad.export_totals(sys.argv[-1])
    except Exception as err:
        logging.error(err)
