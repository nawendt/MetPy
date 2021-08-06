# Copyright (c) 2008,2015,2016,2017,2018,2019 MetPy Developers.
# Distributed under the terms of the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause
"""Test various METARs."""
from datetime import datetime

import numpy as np
from numpy.testing import assert_almost_equal
import pytest

from metpy.cbook import get_test_data
from metpy.io import parse_metar_file, parse_metar_to_dataframe
from metpy.io.metar import Metar, parse_metar
from metpy.units import units


@pytest.mark.parametrize(['metar', 'truth'], [
    # Missing station
    ('METAR KLBG 261155Z AUTO 00000KT 10SM CLR 05/00 A3001 RMK AO2=',
     Metar('KLBG', np.nan, np.nan, np.nan, datetime(2017, 5, 26, 11, 55), 0, 0, 16093.44,
           np.nan, np.nan, np.nan, 'CLR', np.nan, np.nan, np.nan, np.nan, np.nan, np.nan,
           np.nan, 0, 5, 0, 30.01, 0, 0, 0, 'AO2')),
    # Broken clouds
    ('METAR KLOT 261155Z AUTO 00000KT 10SM BKN100 05/00 A3001 RMK AO2=',
     Metar('KLOT', 41.6, -88.1, 205, datetime(2017, 5, 26, 11, 55), 0, 0, 16093.44, np.nan,
           np.nan, np.nan, 'BKN', 10000, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 6, 5,
           0, 30.01, 0, 0, 0, 'AO2')),
    # Few clouds, bad time and winds
    ('METAR KMKE 266155Z AUTO /////KT 10SM FEW100 05/00 A3001 RMK AO2=',
     Metar('KMKE', 42.95, -87.9, 206, np.nan, np.nan, np.nan, 16093.44,
           np.nan, np.nan, np.nan, 'FEW', 10000, np.nan, np.nan, np.nan, np.nan, np.nan,
           np.nan, 2, 5, 0, 30.01, 0, 0, 0, 'AO2')),
    # Many weather and cloud slots taken
    ('METAR RJOI 261155Z 00000KT 4000 -SHRA BR VCSH BKN009 BKN015 OVC030 OVC040 22/21 A2987 '
     'RMK SHRAB35E44 SLP114 VCSH S-NW P0000 60021 70021 T02220206 10256 20211 55000=',
     Metar('RJOI', 34.13, 132.22, 2, datetime(2017, 5, 26, 11, 55), 0, 0, 4000, '-SHRA', 'BR',
           'VCSH', 'BKN', 900, 'BKN', 1500, 'OVC', 3000, 'OVC', 4000, 8, 22, 21, 29.87, 80, 10,
           16, 'SHRAB35E44 SLP114 VCSH S-NW P0000 60021 70021 T02220206 10256 20211 55000')),
    # Smoke for current weather
    ('KFLG 252353Z AUTO 27005KT 10SM FU BKN036 BKN085 22/03 A3018 RMK AO2 SLP130 T02220033 '
     '10250 20217 55007=',
     Metar('KFLG', 35.13, -111.67, 2134, datetime(2017, 5, 25, 23, 53), 270, 5, 16093.44, 'FU',
           np.nan, np.nan, 'BKN', 3600, 'BKN', 8500, np.nan, np.nan, np.nan, np.nan, 6, 22, 3,
           30.18, 4, 0, 0, 'AO2 SLP130 T02220033 10250 20217 55007')),
    # CAVOK for visibility group
    ('METAR OBBI 011200Z 33012KT CAVOK 40/18 Q0997 NOSIG=',
     Metar('OBBI', 26.27, 50.63, 2, datetime(2017, 5, 1, 12, 00), 330, 12, 10000, np.nan,
           np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 0,
           40, 18, units.Quantity(997, 'hPa').m_as('inHg'), 0, 0, 0, 'NOSIG')),
    # Visibility using a mixed fraction
    ('K2I0 011155Z AUTO 05004KT 1 3/4SM BR SCT001 22/22 A3009 RMK AO2 70001 T02210221 10223 '
     '20208=',
     Metar('K2I0', 37.35, -87.4, 134, datetime(2017, 5, 1, 11, 55), 50, 4, 2816.352, 'BR',
           np.nan, np.nan, 'SCT', 100, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 4,
           22, 22, 30.09, 10, 0, 0, 'AO2 70001 T02210221 10223 20208')),
    # Missing temperature
    ('KIOW 011152Z AUTO A3006 RMK AO2 SLPNO 70020 51013 PWINO=',
     Metar('KIOW', 41.63, -91.55, 198, datetime(2017, 5, 1, 11, 52), np.nan, np.nan, np.nan,
           np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan,
           np.nan, 10, np.nan, np.nan, 30.06, 0, 0, 0, 'AO2 SLPNO 70020 51013 PWINO')),
    # Missing data
    ('METAR KBOU 011152Z AUTO 02006KT //// // ////// 42/02 Q1004=',
     Metar('KBOU', 40., -105.33, 1625, datetime(2017, 5, 1, 11, 52), 20, 6, np.nan,
           np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan,
           np.nan, 10, 42, 2, units.Quantity(1004, 'hPa').m_as('inHg'), 0, 0, 0, '')),
    # Vertical visibility
    ('KSLK 011151Z AUTO 21005KT 1/4SM FG VV002 14/13 A1013 RMK AO2 SLP151 70043 T01390133 '
     '10139 20094 53002=',
     Metar('KSLK', 44.4, -74.2, 498, datetime(2017, 5, 1, 11, 51), 210, 5, 402.336, 'FG',
           np.nan, np.nan, 'VV', 200, np.nan, np.nan, np.nan, np.nan, np.nan,
           np.nan, 8, 14, 13, units.Quantity(1013, 'hPa').m_as('inHg'), 45, 0, 0,
           'AO2 SLP151 70043 T01390133 10139 20094 53002')),
    # Missing vertical visibility height
    ('SLCP 011200Z 18008KT 0100 FG VV/// 19/19 Q1019=',
     Metar('SLCP', -16.14, -62.02, 497, datetime(2017, 5, 1, 12, 00), 180, 8, 100, 'FG',
           np.nan, np.nan, 'VV', np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 8, 19,
           19, units.Quantity(1019, 'hPa').m_as('inHg'), 45, 0, 0, '')),
    # BCFG current weather; also visibility is encoding 80SM which we're not adjusting
    ('METAR KMWN 011249Z 36037G45KT 80SM BCFG BKN/// FEW000 07/05 RMK BCFG FEW000 TPS LWR '
     'BKN037 BCFG INTMT=',
     Metar('KMWN', 44.27, -71.3, 1910, datetime(2017, 5, 1, 12, 49), 360, 37,
           units.Quantity(80, 'mi').m_as('m'), 'BCFG', np.nan, np.nan, 'BKN', np.nan,
           'FEW', 0, np.nan, np.nan, np.nan, np.nan, 6, 7, 5, np.nan, 41, 0, 0,
           'BCFG FEW000 TPS LWR BKN037 BCFG INTMT')),
    # -DZ current weather
    ('KULM 011215Z AUTO 22003KT 10SM -DZ CLR 19/19 A3000 RMK AO2=',
     Metar('KULM', 44.32, -94.5, 308, datetime(2017, 5, 1, 12, 15), 220, 3, 16093.44, '-DZ',
           np.nan, np.nan, 'CLR', np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 0,
           19, 19, 30., 51, 0, 0, 'AO2')),
    # CB trailing on cloud group
    ('METAR AGGH 011200Z 25003KT 9999 FEW015 FEW017CB BKN030 25/24 Q1011=',
     Metar('AGGH', -9.42, 160.05, 9, datetime(2017, 5, 1, 12, 00), 250, 3., 9999, np.nan,
           np.nan, np.nan, 'FEW', 1500, 'FEW', 1700, 'BKN', 3000, np.nan, np.nan, 6, 25,
           24, units.Quantity(1011, 'hPa').m_as('inHg'), 0, 0, 0, '')),
    # 5 levels of clouds
    ('METAR KSEQ 011158Z AUTO 08003KT 9SM FEW009 BKN020 BKN120 BKN150 OVC180 22/22 A3007 RMK '
     'AO2 RAB12E46RAB56E57 CIG 020V150 BKN020 V FEW SLP179 P0000 60000 70001 52008=',
     Metar('KSEQ', 29.566666666666666, -97.91666666666667, 160, datetime(2017, 5, 1, 11, 58),
           80, 3., units.Quantity(9, 'miles').m_as('m'), np.nan, np.nan, np.nan, 'FEW', 900.,
           'BKN', 2000., 'BKN', 12000., 'BKN', 15000., 8, 22., 22., 30.07, 0, 0, 0,
           'AO2 RAB12E46RAB56E57 CIG 020V150 BKN020 V FEW SLP179 P0000 60000 70001 52008')),
    # -FZUP
    ('SPECI CBBC 060030Z AUTO 17009G15KT 9SM -FZUP FEW011 SCT019 BKN026 OVC042 02/01 A3004 '
     'RMK ICG INTMT SLP177=',
     Metar('CBBC', 52.18, -128.15, 43, datetime(2017, 5, 6, 0, 30), 170, 9.,
           units.Quantity(9, 'miles').m_as('m'), '-FZUP', np.nan, np.nan, 'FEW', 1100.,
           'SCT', 1900., 'BKN', 2600., 'OVC', 4200., 8, 2, 1, 30.04, 147, 0, 0,
           'ICG INTMT SLP177')),
    # Weird VV group and +SG
    ('BGGH 060750Z AUTO 36004KT 0100NDV +SG VV001/// 05/05 Q1000',
     Metar('BGGH', 64.2, -51.68, 70, datetime(2017, 5, 6, 7, 50), 360, 4, 100, '+SG', np.nan,
           np.nan, 'VV', 100, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 8, 5, 5,
           units.Quantity(1000, 'hPa').m_as('inHg'), 77, 0, 0, '')),
    # COR at beginning, also wind MPS (m/s)
    ('COR ZLLL 101100Z 13010MPS 5000 -SHRA BLDU FEW033CB BKN046 21/11 Q1014 BECMG TL1240 '
     '04004MPS NSW',
     Metar('ZLLL', 36.52, 103.62, 1947, datetime(2017, 5, 10, 11, 0), 130,
           units.Quantity(10, 'm/s').m_as('knots'), 5000, '-SHRA', 'BLDU', np.nan, 'FEW',
           3300, 'BKN', 4600, np.nan, np.nan, np.nan, np.nan, 6, 21, 11,
           units.Quantity(1014, 'hPa').m_as('inHg'), 80, 1007, 0,
           'BECMG TL1240 04004MPS NSW')),
    # M1/4SM vis, -VCTSSN weather
    ('K4BM 020127Z AUTO 04013G24KT 010V080 M1/4SM -VCTSSN OVC002 07/06 A3060 '
     'RMK AO2 LTG DSNT SE THRU SW',
     Metar('K4BM', 39.04, -105.52, 3438, datetime(2017, 5, 2, 1, 27), 40, 13,
           units.Quantity(0.25, 'mi').m_as('m'), '-VCTSSN', np.nan, np.nan, 'OVC', 200,
           np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 8, 7, 6, 30.60, 2095, 0, 0,
           'AO2 LTG DSNT SE THRU SW')),
    # Variable visibility group
    ('ENBS 121620Z 36008KT 9999 3000N VCFG -DZ SCT006 BKN009 12/11 Q1014',
     Metar('ENBS', 70.62, 29.72, 10, datetime(2017, 5, 12, 16, 20), 360, 8, 9999, 'VCFG',
           '-DZ', np.nan, 'SCT', 600, 'BKN', 900, np.nan, np.nan, np.nan, np.nan, 6, 12, 11,
           units.Quantity(1014, 'hPa').m_as('inHg'), 40, 51, 0, '')),
    # More complicated runway visibility
    ('CYYC 030047Z 26008G19KT 170V320 1SM R35L/5500VP6000FT/D R29/P6000FT/D R35R/P6000FT/D '
     '+TSRAGS BR OVC009CB 18/16 A2993 RMK CB8 FRQ LTGIC OVRHD PRESRR SLP127 DENSITY ALT '
     '4800FT',
     Metar('CYYC', 51.12, -114.02, 1084, datetime(2017, 5, 3, 0, 47), 260, 8,
           units.Quantity(1, 'mi').m_as('m'), '+TSRAGS', 'BR', np.nan, 'OVC', 900, np.nan,
           np.nan, np.nan, np.nan, np.nan, np.nan, 8, 18, 16, 29.93, 99, 10, 0,
           'CB8 FRQ LTGIC OVRHD PRESRR SLP127 DENSITY ALT 4800FT'))],
    ids=['missing station', 'BKN', 'FEW', 'current weather', 'smoke', 'CAVOK', 'vis fraction',
         'missing temps', 'missing data', 'vertical vis', 'missing vertical vis', 'BCFG',
         '-DZ', 'sky cover CB', '5 sky levels', '-FZUP', 'VV group', 'COR placement',
         'M1/4SM vis', 'variable vis', 'runway vis'])
def test_metar_parser(metar, truth):
    """Test parsing individual METARs."""
    assert parse_metar(metar, 2017, 5) == truth


def test_date_time_given():
    """Test for when date_time is given."""
    df = parse_metar_to_dataframe('K6B0 261200Z AUTO 00000KT 10SM CLR 20/M17 A3002 RMK AO2 '
                                  'T01990165=', year=2019, month=6)
    assert df.date_time[0] == datetime(2019, 6, 26, 12)
    assert df.eastward_wind[0] == 0
    assert df.northward_wind[0] == 0
    assert_almost_equal(df.air_pressure_at_sea_level[0], 1016.56)
    assert_almost_equal(df.visibility.values, 16093.44)


def test_parse_metar_df_positional_datetime_failure():
    """Test that positional year, month arguments fail for parse_metar_to_dataframe."""
    # pylint: disable=too-many-function-args
    with pytest.raises(TypeError, match='takes 1 positional argument but 3 were given'):
        parse_metar_to_dataframe('K6B0 261200Z AUTO 00000KT 10SM CLR 20/M17'
                                 'A3002 RMK AO2 T01990165=', 2019, 6)


def test_parse_metar_to_dataframe():
    """Test parsing a single METAR to a DataFrame."""
    df = parse_metar_to_dataframe('KDEN 012153Z 09010KT 10SM FEW060 BKN110 BKN220 27/13 '
                                  'A3010 RMK AO2 LTG DSNT SW AND W SLP114 OCNL LTGICCG '
                                  'DSNT SW CB DSNT SW MOV E T02670128')
    assert df.wind_direction.values == 90
    assert df.wind_speed.values == 10
    assert_almost_equal(df.eastward_wind.values, -10)
    assert_almost_equal(df.northward_wind.values, 0)
    assert_almost_equal(df.visibility.values, 16093.44)
    assert df.air_temperature.values == 27
    assert df.dew_point_temperature.values == 13


def test_parse_file():
    """Test the parser on an entire file."""
    input_file = get_test_data('metar_20190701_1200.txt', as_file_obj=False)
    df = parse_metar_file(input_file)

    # Check counts (non-NaN) of various fields
    counts = df.count()
    assert counts.station_id == 8980
    assert counts.latitude == 8968
    assert counts.longitude == 8968
    assert counts.elevation == 8968
    assert counts.date_time == 8980
    assert counts.wind_direction == 8577
    assert counts.wind_speed == 8844
    assert counts.visibility == 8458
    assert counts.current_wx1 == 1046
    assert counts.current_wx2 == 77
    assert counts.current_wx3 == 1
    assert counts.low_cloud_type == 7309
    assert counts.low_cloud_level == 3821
    assert counts.medium_cloud_type == 1629
    assert counts.medium_cloud_level == 1624
    assert counts.high_cloud_type == 626
    assert counts.high_cloud_level == 620
    assert counts.highest_cloud_type == 37
    assert counts.highest_cloud_level == 37
    assert counts.cloud_coverage == 8980
    assert counts.air_temperature == 8727
    assert counts.dew_point_temperature == 8707
    assert counts.altimeter == 8400
    assert counts.remarks == 8980
    assert (df.current_wx1_symbol != 0).sum() == counts.current_wx1
    assert (df.current_wx2_symbol != 0).sum() == counts.current_wx2
    assert (df.current_wx3_symbol != 0).sum() == counts.current_wx3
    assert counts.air_pressure_at_sea_level == 8328
    assert counts.eastward_wind == 8577
    assert counts.northward_wind == 8577

    # KVPZ 011156Z AUTO 27005KT 10SM CLR 23/19 A3004 RMK AO2 SLP166
    test = df[df.station_id == 'KVPZ']
    assert test.air_temperature.values == 23
    assert test.dew_point_temperature.values == 19
    assert test.altimeter.values == 30.04
    assert_almost_equal(test.eastward_wind.values, 5)
    assert_almost_equal(test.northward_wind.values, 0)
    assert test.air_pressure_at_sea_level.values == 1016.76

    # Check that this ob properly gets all lines
    paku = df[df.station_id == 'PAKU']
    assert_almost_equal(paku.air_temperature.values, [9, 12])
    assert_almost_equal(paku.dew_point_temperature.values, [9, 10])
    assert_almost_equal(paku.altimeter.values, [30.02, 30.04])


def test_parse_file_positional_datetime_failure():
    """Test that positional year, month arguments fail for parse_metar_file."""
    # pylint: disable=too-many-function-args
    input_file = get_test_data('metar_20190701_1200.txt', as_file_obj=False)
    with pytest.raises(TypeError, match='takes 1 positional argument but 3 were given'):
        parse_metar_file(input_file, 2016, 12)


def test_parse_file_bad_encoding():
    """Test the parser on an entire file that has at least one bad utf-8 encoding."""
    input_file = get_test_data('2020010600_sao.wmo', as_file_obj=False)
    # KDEN 052353Z 16014KT 10SM FEW120 FEW220 02/M07 A3008 RMK AO2 SLP190 T00171072...
    df = parse_metar_file(input_file)

    # Check counts (non-NaN) of various fields
    counts = df.count()
    assert counts.station_id == 8802
    assert counts.latitude == 8789
    assert counts.longitude == 8789
    assert counts.elevation == 8789
    assert counts.date_time == 8802
    assert counts.wind_direction == 8377
    assert counts.wind_speed == 8673
    assert counts.visibility == 8304
    assert counts.current_wx1 == 1274
    assert counts.current_wx2 == 201
    assert counts.current_wx3 == 3
    assert counts.low_cloud_type == 7516
    assert counts.low_cloud_level == 3715
    assert counts.medium_cloud_type == 1612
    assert counts.medium_cloud_level == 1603
    assert counts.high_cloud_type == 542
    assert counts.high_cloud_level == 541
    assert counts.highest_cloud_type == 40
    assert counts.highest_cloud_level == 40
    assert counts.cloud_coverage == 8802
    assert counts.air_temperature == 8444
    assert counts.dew_point_temperature == 8383
    assert counts.altimeter == 8108
    assert counts.remarks == 8802
    assert (df.current_wx1_symbol != 0).sum() == counts.current_wx1
    assert (df.current_wx2_symbol != 0).sum() == counts.current_wx2
    assert (df.current_wx3_symbol != 0).sum() == counts.current_wx3
    assert counts.air_pressure_at_sea_level == 8069
    assert counts.eastward_wind == 8377
    assert counts.northward_wind == 8377

    test = df[df.station_id == 'KDEN']
    assert_almost_equal(test.visibility.values, 16093.44)
    assert test.air_temperature.values == 2
    assert test.air_pressure_at_sea_level.values == 1024.71


def test_parse_file_object():
    """Test the parser reading from a file-like object."""
    input_file = get_test_data('metar_20190701_1200.txt', mode='rt')
    # KOKC 011152Z 18006KT 7SM FEW080 FEW250 21/21 A3003 RMK AO2 SLP155 T02060206...
    df = parse_metar_file(input_file)
    test = df[df.station_id == 'KOKC']
    assert_almost_equal(test.visibility.values, 11265.408)
    assert test.air_temperature.values == 21
    assert test.dew_point_temperature.values == 21
    assert test.altimeter.values == 30.03
    assert_almost_equal(test.eastward_wind.values, 0)
    assert_almost_equal(test.northward_wind.values, 6)


def test_parse_no_pint_objects_in_df():
    """Test that there are no Pint quantities in dataframes created by parser."""
    input_file = get_test_data('metar_20190701_1200.txt', mode='rt')
    metar_str = ('KSLK 011151Z AUTO 21005KT 1/4SM FG VV002 14/13 A1013 RMK AO2 SLP151 70043 '
                 'T01390133 10139 20094 53002=')

    for df in (parse_metar_file(input_file), parse_metar_to_dataframe(metar_str)):
        for column in df:
            assert not isinstance(df[column][0], units.Quantity)
