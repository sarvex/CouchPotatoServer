# -*- coding: utf-8 -*-
# Copyright 2011-2012 Antoine Bertin <diaoulael@gmail.com>
#
# This file is part of subliminal.
#
# subliminal is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# subliminal is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with subliminal.  If not, see <http://www.gnu.org/licenses/>.
import logging
import re

from .utils import to_unicode

logger = logging.getLogger(__name__)

COUNTRIES = [('AF', 'AFG', '004', 'Afghanistan'),
             ('AX', 'ALA', '248', 'Åland Islands'),
             ('AL', 'ALB', '008', 'Albania'),
             ('DZ', 'DZA', '012', 'Algeria'),
             ('AS', 'ASM', '016', 'American Samoa'),
             ('AD', 'AND', '020', 'Andorra'),
             ('AO', 'AGO', '024', 'Angola'),
             ('AI', 'AIA', '660', 'Anguilla'),
             ('AQ', 'ATA', '010', 'Antarctica'),
             ('AG', 'ATG', '028', 'Antigua and Barbuda'),
             ('AR', 'ARG', '032', 'Argentina'),
             ('AM', 'ARM', '051', 'Armenia'),
             ('AW', 'ABW', '533', 'Aruba'),
             ('AU', 'AUS', '036', 'Australia'),
             ('AT', 'AUT', '040', 'Austria'),
             ('AZ', 'AZE', '031', 'Azerbaijan'),
             ('BS', 'BHS', '044', 'Bahamas'),
             ('BH', 'BHR', '048', 'Bahrain'),
             ('BD', 'BGD', '050', 'Bangladesh'),
             ('BB', 'BRB', '052', 'Barbados'),
             ('BY', 'BLR', '112', 'Belarus'),
             ('BE', 'BEL', '056', 'Belgium'),
             ('BZ', 'BLZ', '084', 'Belize'),
             ('BJ', 'BEN', '204', 'Benin'),
             ('BM', 'BMU', '060', 'Bermuda'),
             ('BT', 'BTN', '064', 'Bhutan'),
             ('BO', 'BOL', '068', 'Bolivia, Plurinational State of'),
             ('BQ', 'BES', '535', 'Bonaire, Sint Eustatius and Saba'),
             ('BA', 'BIH', '070', 'Bosnia and Herzegovina'),
             ('BW', 'BWA', '072', 'Botswana'),
             ('BV', 'BVT', '074', 'Bouvet Island'),
             ('BR', 'BRA', '076', 'Brazil'),
             ('IO', 'IOT', '086', 'British Indian Ocean Territory'),
             ('BN', 'BRN', '096', 'Brunei Darussalam'),
             ('BG', 'BGR', '100', 'Bulgaria'),
             ('BF', 'BFA', '854', 'Burkina Faso'),
             ('BI', 'BDI', '108', 'Burundi'),
             ('KH', 'KHM', '116', 'Cambodia'),
             ('CM', 'CMR', '120', 'Cameroon'),
             ('CA', 'CAN', '124', 'Canada'),
             ('CV', 'CPV', '132', 'Cape Verde'),
             ('KY', 'CYM', '136', 'Cayman Islands'),
             ('CF', 'CAF', '140', 'Central African Republic'),
             ('TD', 'TCD', '148', 'Chad'),
             ('CL', 'CHL', '152', 'Chile'),
             ('CN', 'CHN', '156', 'China'),
             ('CX', 'CXR', '162', 'Christmas Island'),
             ('CC', 'CCK', '166', 'Cocos (Keeling) Islands'),
             ('CO', 'COL', '170', 'Colombia'),
             ('KM', 'COM', '174', 'Comoros'),
             ('CG', 'COG', '178', 'Congo'),
             ('CD', 'COD', '180', 'Congo, The Democratic Republic of the'),
             ('CK', 'COK', '184', 'Cook Islands'),
             ('CR', 'CRI', '188', 'Costa Rica'),
             ('CI', 'CIV', '384', 'Côte d\'Ivoire'),
             ('HR', 'HRV', '191', 'Croatia'),
             ('CU', 'CUB', '192', 'Cuba'),
             ('CW', 'CUW', '531', 'Curaçao'),
             ('CY', 'CYP', '196', 'Cyprus'),
             ('CZ', 'CZE', '203', 'Czech Republic'),
             ('DK', 'DNK', '208', 'Denmark'),
             ('DJ', 'DJI', '262', 'Djibouti'),
             ('DM', 'DMA', '212', 'Dominica'),
             ('DO', 'DOM', '214', 'Dominican Republic'),
             ('EC', 'ECU', '218', 'Ecuador'),
             ('EG', 'EGY', '818', 'Egypt'),
             ('SV', 'SLV', '222', 'El Salvador'),
             ('GQ', 'GNQ', '226', 'Equatorial Guinea'),
             ('ER', 'ERI', '232', 'Eritrea'),
             ('EE', 'EST', '233', 'Estonia'),
             ('ET', 'ETH', '231', 'Ethiopia'),
             ('FK', 'FLK', '238', 'Falkland Islands (Malvinas)'),
             ('FO', 'FRO', '234', 'Faroe Islands'),
             ('FJ', 'FJI', '242', 'Fiji'),
             ('FI', 'FIN', '246', 'Finland'),
             ('FR', 'FRA', '250', 'France'),
             ('GF', 'GUF', '254', 'French Guiana'),
             ('PF', 'PYF', '258', 'French Polynesia'),
             ('TF', 'ATF', '260', 'French Southern Territories'),
             ('GA', 'GAB', '266', 'Gabon'),
             ('GM', 'GMB', '270', 'Gambia'),
             ('GE', 'GEO', '268', 'Georgia'),
             ('DE', 'DEU', '276', 'Germany'),
             ('GH', 'GHA', '288', 'Ghana'),
             ('GI', 'GIB', '292', 'Gibraltar'),
             ('GR', 'GRC', '300', 'Greece'),
             ('GL', 'GRL', '304', 'Greenland'),
             ('GD', 'GRD', '308', 'Grenada'),
             ('GP', 'GLP', '312', 'Guadeloupe'),
             ('GU', 'GUM', '316', 'Guam'),
             ('GT', 'GTM', '320', 'Guatemala'),
             ('GG', 'GGY', '831', 'Guernsey'),
             ('GN', 'GIN', '324', 'Guinea'),
             ('GW', 'GNB', '624', 'Guinea-Bissau'),
             ('GY', 'GUY', '328', 'Guyana'),
             ('HT', 'HTI', '332', 'Haiti'),
             ('HM', 'HMD', '334', 'Heard Island and McDonald Islands'),
             ('VA', 'VAT', '336', 'Holy See (Vatican City State)'),
             ('HN', 'HND', '340', 'Honduras'),
             ('HK', 'HKG', '344', 'Hong Kong'),
             ('HU', 'HUN', '348', 'Hungary'),
             ('IS', 'ISL', '352', 'Iceland'),
             ('IN', 'IND', '356', 'India'),
             ('ID', 'IDN', '360', 'Indonesia'),
             ('IR', 'IRN', '364', 'Iran, Islamic Republic of'),
             ('IQ', 'IRQ', '368', 'Iraq'),
             ('IE', 'IRL', '372', 'Ireland'),
             ('IM', 'IMN', '833', 'Isle of Man'),
             ('IL', 'ISR', '376', 'Israel'),
             ('IT', 'ITA', '380', 'Italy'),
             ('JM', 'JAM', '388', 'Jamaica'),
             ('JP', 'JPN', '392', 'Japan'),
             ('JE', 'JEY', '832', 'Jersey'),
             ('JO', 'JOR', '400', 'Jordan'),
             ('KZ', 'KAZ', '398', 'Kazakhstan'),
             ('KE', 'KEN', '404', 'Kenya'),
             ('KI', 'KIR', '296', 'Kiribati'),
             ('KP', 'PRK', '408', 'Korea, Democratic People\'s Republic of'),
             ('KR', 'KOR', '410', 'Korea, Republic of'),
             ('KW', 'KWT', '414', 'Kuwait'),
             ('KG', 'KGZ', '417', 'Kyrgyzstan'),
             ('LA', 'LAO', '418', 'Lao People\'s Democratic Republic'),
             ('LV', 'LVA', '428', 'Latvia'),
             ('LB', 'LBN', '422', 'Lebanon'),
             ('LS', 'LSO', '426', 'Lesotho'),
             ('LR', 'LBR', '430', 'Liberia'),
             ('LY', 'LBY', '434', 'Libya'),
             ('LI', 'LIE', '438', 'Liechtenstein'),
             ('LT', 'LTU', '440', 'Lithuania'),
             ('LU', 'LUX', '442', 'Luxembourg'),
             ('MO', 'MAC', '446', 'Macao'),
             ('MK', 'MKD', '807', 'Macedonia, Republic of'),
             ('MG', 'MDG', '450', 'Madagascar'),
             ('MW', 'MWI', '454', 'Malawi'),
             ('MY', 'MYS', '458', 'Malaysia'),
             ('MV', 'MDV', '462', 'Maldives'),
             ('ML', 'MLI', '466', 'Mali'),
             ('MT', 'MLT', '470', 'Malta'),
             ('MH', 'MHL', '584', 'Marshall Islands'),
             ('MQ', 'MTQ', '474', 'Martinique'),
             ('MR', 'MRT', '478', 'Mauritania'),
             ('MU', 'MUS', '480', 'Mauritius'),
             ('YT', 'MYT', '175', 'Mayotte'),
             ('MX', 'MEX', '484', 'Mexico'),
             ('FM', 'FSM', '583', 'Micronesia, Federated States of'),
             ('MD', 'MDA', '498', 'Moldova, Republic of'),
             ('MC', 'MCO', '492', 'Monaco'),
             ('MN', 'MNG', '496', 'Mongolia'),
             ('ME', 'MNE', '499', 'Montenegro'),
             ('MS', 'MSR', '500', 'Montserrat'),
             ('MA', 'MAR', '504', 'Morocco'),
             ('MZ', 'MOZ', '508', 'Mozambique'),
             ('MM', 'MMR', '104', 'Myanmar'),
             ('NA', 'NAM', '516', 'Namibia'),
             ('NR', 'NRU', '520', 'Nauru'),
             ('NP', 'NPL', '524', 'Nepal'),
             ('NL', 'NLD', '528', 'Netherlands'),
             ('NC', 'NCL', '540', 'New Caledonia'),
             ('NZ', 'NZL', '554', 'New Zealand'),
             ('NI', 'NIC', '558', 'Nicaragua'),
             ('NE', 'NER', '562', 'Niger'),
             ('NG', 'NGA', '566', 'Nigeria'),
             ('NU', 'NIU', '570', 'Niue'),
             ('NF', 'NFK', '574', 'Norfolk Island'),
             ('MP', 'MNP', '580', 'Northern Mariana Islands'),
             ('NO', 'NOR', '578', 'Norway'),
             ('OM', 'OMN', '512', 'Oman'),
             ('PK', 'PAK', '586', 'Pakistan'),
             ('PW', 'PLW', '585', 'Palau'),
             ('PS', 'PSE', '275', 'Palestinian Territory, Occupied'),
             ('PA', 'PAN', '591', 'Panama'),
             ('PG', 'PNG', '598', 'Papua New Guinea'),
             ('PY', 'PRY', '600', 'Paraguay'),
             ('PE', 'PER', '604', 'Peru'),
             ('PH', 'PHL', '608', 'Philippines'),
             ('PN', 'PCN', '612', 'Pitcairn'),
             ('PL', 'POL', '616', 'Poland'),
             ('PT', 'PRT', '620', 'Portugal'),
             ('PR', 'PRI', '630', 'Puerto Rico'),
             ('QA', 'QAT', '634', 'Qatar'),
             ('RE', 'REU', '638', 'Réunion'),
             ('RO', 'ROU', '642', 'Romania'),
             ('RU', 'RUS', '643', 'Russian Federation'),
             ('RW', 'RWA', '646', 'Rwanda'),
             ('BL', 'BLM', '652', 'Saint Barthélemy'),
             ('SH', 'SHN', '654', 'Saint Helena, Ascension and Tristan da Cunha'),
             ('KN', 'KNA', '659', 'Saint Kitts and Nevis'),
             ('LC', 'LCA', '662', 'Saint Lucia'),
             ('MF', 'MAF', '663', 'Saint Martin (French part)'),
             ('PM', 'SPM', '666', 'Saint Pierre and Miquelon'),
             ('VC', 'VCT', '670', 'Saint Vincent and the Grenadines'),
             ('WS', 'WSM', '882', 'Samoa'),
             ('SM', 'SMR', '674', 'San Marino'),
             ('ST', 'STP', '678', 'Sao Tome and Principe'),
             ('SA', 'SAU', '682', 'Saudi Arabia'),
             ('SN', 'SEN', '686', 'Senegal'),
             ('RS', 'SRB', '688', 'Serbia'),
             ('SC', 'SYC', '690', 'Seychelles'),
             ('SL', 'SLE', '694', 'Sierra Leone'),
             ('SG', 'SGP', '702', 'Singapore'),
             ('SX', 'SXM', '534', 'Sint Maarten (Dutch part)'),
             ('SK', 'SVK', '703', 'Slovakia'),
             ('SI', 'SVN', '705', 'Slovenia'),
             ('SB', 'SLB', '090', 'Solomon Islands'),
             ('SO', 'SOM', '706', 'Somalia'),
             ('ZA', 'ZAF', '710', 'South Africa'),
             ('GS', 'SGS', '239', 'South Georgia and the South Sandwich Islands'),
             ('ES', 'ESP', '724', 'Spain'),
             ('LK', 'LKA', '144', 'Sri Lanka'),
             ('SD', 'SDN', '729', 'Sudan'),
             ('SR', 'SUR', '740', 'Suriname'),
             ('SS', 'SSD', '728', 'South Sudan'),
             ('SJ', 'SJM', '744', 'Svalbard and Jan Mayen'),
             ('SZ', 'SWZ', '748', 'Swaziland'),
             ('SE', 'SWE', '752', 'Sweden'),
             ('CH', 'CHE', '756', 'Switzerland'),
             ('SY', 'SYR', '760', 'Syrian Arab Republic'),
             ('TW', 'TWN', '158', 'Taiwan, Province of China'),
             ('TJ', 'TJK', '762', 'Tajikistan'),
             ('TZ', 'TZA', '834', 'Tanzania, United Republic of'),
             ('TH', 'THA', '764', 'Thailand'),
             ('TL', 'TLS', '626', 'Timor-Leste'),
             ('TG', 'TGO', '768', 'Togo'),
             ('TK', 'TKL', '772', 'Tokelau'),
             ('TO', 'TON', '776', 'Tonga'),
             ('TT', 'TTO', '780', 'Trinidad and Tobago'),
             ('TN', 'TUN', '788', 'Tunisia'),
             ('TR', 'TUR', '792', 'Turkey'),
             ('TM', 'TKM', '795', 'Turkmenistan'),
             ('TC', 'TCA', '796', 'Turks and Caicos Islands'),
             ('TV', 'TUV', '798', 'Tuvalu'),
             ('UG', 'UGA', '800', 'Uganda'),
             ('UA', 'UKR', '804', 'Ukraine'),
             ('AE', 'ARE', '784', 'United Arab Emirates'),
             ('GB', 'GBR', '826', 'United Kingdom'),
             ('US', 'USA', '840', 'United States'),
             ('UM', 'UMI', '581', 'United States Minor Outlying Islands'),
             ('UY', 'URY', '858', 'Uruguay'),
             ('UZ', 'UZB', '860', 'Uzbekistan'),
             ('VU', 'VUT', '548', 'Vanuatu'),
             ('VE', 'VEN', '862', 'Venezuela, Bolivarian Republic of'),
             ('VN', 'VNM', '704', 'Viet Nam'),
             ('VG', 'VGB', '092', 'Virgin Islands, British'),
             ('VI', 'VIR', '850', 'Virgin Islands, U.S.'),
             ('WF', 'WLF', '876', 'Wallis and Futuna'),
             ('EH', 'ESH', '732', 'Western Sahara'),
             ('YE', 'YEM', '887', 'Yemen'),
             ('ZM', 'ZMB', '894', 'Zambia'),
             ('ZW', 'ZWE', '716', 'Zimbabwe')]

LANGUAGES = [('aar', '', 'aa', 'Afar', 'afar'),
             ('abk', '', 'ab', 'Abkhazian', 'abkhaze'),
             ('ace', '', '', 'Achinese', 'aceh'),
             ('ach', '', '', 'Acoli', 'acoli'),
             ('ada', '', '', 'Adangme', 'adangme'),
             ('ady', '', '', 'Adyghe; Adygei', 'adyghé'),
             ('afa', '', '', 'Afro-Asiatic languages', 'afro-asiatiques, langues'),
             ('afh', '', '', 'Afrihili', 'afrihili'),
             ('afr', '', 'af', 'Afrikaans', 'afrikaans'),
             ('ain', '', '', 'Ainu', 'aïnou'),
             ('aka', '', 'ak', 'Akan', 'akan'),
             ('akk', '', '', 'Akkadian', 'akkadien'),
             ('alb', 'sqi', 'sq', 'Albanian', 'albanais'),
             ('ale', '', '', 'Aleut', 'aléoute'),
             ('alg', '', '', 'Algonquian languages', 'algonquines, langues'),
             ('alt', '', '', 'Southern Altai', 'altai du Sud'),
             ('amh', '', 'am', 'Amharic', 'amharique'),
             ('ang', '', '', 'English, Old (ca.450-1100)', 'anglo-saxon (ca.450-1100)'),
             ('anp', '', '', 'Angika', 'angika'),
             ('apa', '', '', 'Apache languages', 'apaches, langues'),
             ('ara', '', 'ar', 'Arabic', 'arabe'),
             ('arc', '', '', 'Official Aramaic (700-300 BCE); Imperial Aramaic (700-300 BCE)',
              'araméen d\'empire (700-300 BCE)'),
             ('arg', '', 'an', 'Aragonese', 'aragonais'),
             ('arm', 'hye', 'hy', 'Armenian', 'arménien'),
             ('arn', '', '', 'Mapudungun; Mapuche', 'mapudungun; mapuche; mapuce'),
             ('arp', '', '', 'Arapaho', 'arapaho'),
             ('art', '', '', 'Artificial languages', 'artificielles, langues'),
             ('arw', '', '', 'Arawak', 'arawak'),
             ('asm', '', 'as', 'Assamese', 'assamais'),
             ('ast', '', '', 'Asturian; Bable; Leonese; Asturleonese', 'asturien; bable; léonais; asturoléonais'),
             ('ath', '', '', 'Athapascan languages', 'athapascanes, langues'),
             ('aus', '', '', 'Australian languages', 'australiennes, langues'),
             ('ava', '', 'av', 'Avaric', 'avar'),
             ('ave', '', 'ae', 'Avestan', 'avestique'),
             ('awa', '', '', 'Awadhi', 'awadhi'),
             ('aym', '', 'ay', 'Aymara', 'aymara'),
             ('aze', '', 'az', 'Azerbaijani', 'azéri'),
             ('bad', '', '', 'Banda languages', 'banda, langues'),
             ('bai', '', '', 'Bamileke languages', 'bamiléké, langues'),
             ('bak', '', 'ba', 'Bashkir', 'bachkir'),
             ('bal', '', '', 'Baluchi', 'baloutchi'),
             ('bam', '', 'bm', 'Bambara', 'bambara'),
             ('ban', '', '', 'Balinese', 'balinais'),
             ('baq', 'eus', 'eu', 'Basque', 'basque'),
             ('bas', '', '', 'Basa', 'basa'),
             ('bat', '', '', 'Baltic languages', 'baltes, langues'),
             ('bej', '', '', 'Beja; Bedawiyet', 'bedja'),
             ('bel', '', 'be', 'Belarusian', 'biélorusse'),
             ('bem', '', '', 'Bemba', 'bemba'),
             ('ben', '', 'bn', 'Bengali', 'bengali'),
             ('ber', '', '', 'Berber languages', 'berbères, langues'),
             ('bho', '', '', 'Bhojpuri', 'bhojpuri'),
             ('bih', '', 'bh', 'Bihari languages', 'langues biharis'),
             ('bik', '', '', 'Bikol', 'bikol'),
             ('bin', '', '', 'Bini; Edo', 'bini; edo'),
             ('bis', '', 'bi', 'Bislama', 'bichlamar'),
             ('bla', '', '', 'Siksika', 'blackfoot'),
             ('bnt', '', '', 'Bantu (Other)', 'bantoues, autres langues'),
             ('bos', '', 'bs', 'Bosnian', 'bosniaque'),
             ('bra', '', '', 'Braj', 'braj'),
             ('bre', '', 'br', 'Breton', 'breton'),
             ('btk', '', '', 'Batak languages', 'batak, langues'),
             ('bua', '', '', 'Buriat', 'bouriate'),
             ('bug', '', '', 'Buginese', 'bugi'),
             ('bul', '', 'bg', 'Bulgarian', 'bulgare'),
             ('bur', 'mya', 'my', 'Burmese', 'birman'),
             ('byn', '', '', 'Blin; Bilin', 'blin; bilen'),
             ('cad', '', '', 'Caddo', 'caddo'),
             ('cai', '', '', 'Central American Indian languages', 'amérindiennes de L\'Amérique centrale, langues'),
             ('car', '', '', 'Galibi Carib', 'karib; galibi; carib'),
             ('cat', '', 'ca', 'Catalan; Valencian', 'catalan; valencien'),
             ('cau', '', '', 'Caucasian languages', 'caucasiennes, langues'),
             ('ceb', '', '', 'Cebuano', 'cebuano'),
             ('cel', '', '', 'Celtic languages', 'celtiques, langues; celtes, langues'),
             ('cha', '', 'ch', 'Chamorro', 'chamorro'),
             ('chb', '', '', 'Chibcha', 'chibcha'),
             ('che', '', 'ce', 'Chechen', 'tchétchène'),
             ('chg', '', '', 'Chagatai', 'djaghataï'),
             ('chi', 'zho', 'zh', 'Chinese', 'chinois'),
             ('chk', '', '', 'Chuukese', 'chuuk'),
             ('chm', '', '', 'Mari', 'mari'),
             ('chn', '', '', 'Chinook jargon', 'chinook, jargon'),
             ('cho', '', '', 'Choctaw', 'choctaw'),
             ('chp', '', '', 'Chipewyan; Dene Suline', 'chipewyan'),
             ('chr', '', '', 'Cherokee', 'cherokee'),
             ('chu', '', 'cu', 'Church Slavic; Old Slavonic; Church Slavonic; Old Bulgarian; Old Church Slavonic',
              'slavon d\'église; vieux slave; slavon liturgique; vieux bulgare'),
             ('chv', '', 'cv', 'Chuvash', 'tchouvache'),
             ('chy', '', '', 'Cheyenne', 'cheyenne'),
             ('cmc', '', '', 'Chamic languages', 'chames, langues'),
             ('cop', '', '', 'Coptic', 'copte'),
             ('cor', '', 'kw', 'Cornish', 'cornique'),
             ('cos', '', 'co', 'Corsican', 'corse'),
             ('cpe', '', '', 'Creoles and pidgins, English based', 'créoles et pidgins basés sur l\'anglais'),
             ('cpf', '', '', 'Creoles and pidgins, French-based ', 'créoles et pidgins basés sur le français'),
             ('cpp', '', '', 'Creoles and pidgins, Portuguese-based ', 'créoles et pidgins basés sur le portugais'),
             ('cre', '', 'cr', 'Cree', 'cree'),
             ('crh', '', '', 'Crimean Tatar; Crimean Turkish', 'tatar de Crimé'),
             ('crp', '', '', 'Creoles and pidgins ', 'créoles et pidgins'),
             ('csb', '', '', 'Kashubian', 'kachoube'),
             ('cus', '', '', 'Cushitic languages', 'couchitiques, langues'),
             ('cze', 'ces', 'cs', 'Czech', 'tchèque'),
             ('dak', '', '', 'Dakota', 'dakota'),
             ('dan', '', 'da', 'Danish', 'danois'),
             ('dar', '', '', 'Dargwa', 'dargwa'),
             ('day', '', '', 'Land Dayak languages', 'dayak, langues'),
             ('del', '', '', 'Delaware', 'delaware'),
             ('den', '', '', 'Slave (Athapascan)', 'esclave (athapascan)'),
             ('dgr', '', '', 'Dogrib', 'dogrib'),
             ('din', '', '', 'Dinka', 'dinka'),
             ('div', '', 'dv', 'Divehi; Dhivehi; Maldivian', 'maldivien'),
             ('doi', '', '', 'Dogri', 'dogri'),
             ('dra', '', '', 'Dravidian languages', 'dravidiennes, langues'),
             ('dsb', '', '', 'Lower Sorbian', 'bas-sorabe'),
             ('dua', '', '', 'Duala', 'douala'),
             ('dum', '', '', 'Dutch, Middle (ca.1050-1350)', 'néerlandais moyen (ca. 1050-1350)'),
             ('dut', 'nld', 'nl', 'Dutch; Flemish', 'néerlandais; flamand'),
             ('dyu', '', '', 'Dyula', 'dioula'),
             ('dzo', '', 'dz', 'Dzongkha', 'dzongkha'),
             ('efi', '', '', 'Efik', 'efik'),
             ('egy', '', '', 'Egyptian (Ancient)', 'égyptien'),
             ('eka', '', '', 'Ekajuk', 'ekajuk'),
             ('elx', '', '', 'Elamite', 'élamite'),
             ('eng', '', 'en', 'English', 'anglais'),
             ('enm', '', '', 'English, Middle (1100-1500)', 'anglais moyen (1100-1500)'),
             ('epo', '', 'eo', 'Esperanto', 'espéranto'),
             ('est', '', 'et', 'Estonian', 'estonien'),
             ('ewe', '', 'ee', 'Ewe', 'éwé'),
             ('ewo', '', '', 'Ewondo', 'éwondo'),
             ('fan', '', '', 'Fang', 'fang'),
             ('fao', '', 'fo', 'Faroese', 'féroïen'),
             ('fat', '', '', 'Fanti', 'fanti'),
             ('fij', '', 'fj', 'Fijian', 'fidjien'),
             ('fil', '', '', 'Filipino; Pilipino', 'filipino; pilipino'),
             ('fin', '', 'fi', 'Finnish', 'finnois'),
             ('fiu', '', '', 'Finno-Ugrian languages', 'finno-ougriennes, langues'),
             ('fon', '', '', 'Fon', 'fon'),
             ('fre', 'fra', 'fr', 'French', 'français'),
             ('frm', '', '', 'French, Middle (ca.1400-1600)', 'français moyen (1400-1600)'),
             ('fro', '', '', 'French, Old (842-ca.1400)', 'français ancien (842-ca.1400)'),
             ('frr', '', '', 'Northern Frisian', 'frison septentrional'),
             ('frs', '', '', 'Eastern Frisian', 'frison oriental'),
             ('fry', '', 'fy', 'Western Frisian', 'frison occidental'),
             ('ful', '', 'ff', 'Fulah', 'peul'),
             ('fur', '', '', 'Friulian', 'frioulan'),
             ('gaa', '', '', 'Ga', 'ga'),
             ('gay', '', '', 'Gayo', 'gayo'),
             ('gba', '', '', 'Gbaya', 'gbaya'),
             ('gem', '', '', 'Germanic languages', 'germaniques, langues'),
             ('geo', 'kat', 'ka', 'Georgian', 'géorgien'),
             ('ger', 'deu', 'de', 'German', 'allemand'),
             ('gez', '', '', 'Geez', 'guèze'),
             ('gil', '', '', 'Gilbertese', 'kiribati'),
             ('gla', '', 'gd', 'Gaelic; Scottish Gaelic', 'gaélique; gaélique écossais'),
             ('gle', '', 'ga', 'Irish', 'irlandais'),
             ('glg', '', 'gl', 'Galician', 'galicien'),
             ('glv', '', 'gv', 'Manx', 'manx; mannois'),
             ('gmh', '', '', 'German, Middle High (ca.1050-1500)', 'allemand, moyen haut (ca. 1050-1500)'),
             ('goh', '', '', 'German, Old High (ca.750-1050)', 'allemand, vieux haut (ca. 750-1050)'),
             ('gon', '', '', 'Gondi', 'gond'),
             ('gor', '', '', 'Gorontalo', 'gorontalo'),
             ('got', '', '', 'Gothic', 'gothique'),
             ('grb', '', '', 'Grebo', 'grebo'),
             ('grc', '', '', 'Greek, Ancient (to 1453)', 'grec ancien (jusqu\'à 1453)'),
             ('gre', 'ell', 'el', 'Greek, Modern (1453-)', 'grec moderne (après 1453)'),
             ('grn', '', 'gn', 'Guarani', 'guarani'),
             ('gsw', '', '', 'Swiss German; Alemannic; Alsatian', 'suisse alémanique; alémanique; alsacien'),
             ('guj', '', 'gu', 'Gujarati', 'goudjrati'),
             ('gwi', '', '', 'Gwich\'in', 'gwich\'in'),
             ('hai', '', '', 'Haida', 'haida'),
             ('hat', '', 'ht', 'Haitian; Haitian Creole', 'haïtien; créole haïtien'),
             ('hau', '', 'ha', 'Hausa', 'haoussa'),
             ('haw', '', '', 'Hawaiian', 'hawaïen'),
             ('heb', '', 'he', 'Hebrew', 'hébreu'),
             ('her', '', 'hz', 'Herero', 'herero'),
             ('hil', '', '', 'Hiligaynon', 'hiligaynon'),
             ('him', '', '', 'Himachali languages; Western Pahari languages',
              'langues himachalis; langues paharis occidentales'),
             ('hin', '', 'hi', 'Hindi', 'hindi'),
             ('hit', '', '', 'Hittite', 'hittite'),
             ('hmn', '', '', 'Hmong; Mong', 'hmong'),
             ('hmo', '', 'ho', 'Hiri Motu', 'hiri motu'),
             ('hrv', '', 'hr', 'Croatian', 'croate'),
             ('hsb', '', '', 'Upper Sorbian', 'haut-sorabe'),
             ('hun', '', 'hu', 'Hungarian', 'hongrois'),
             ('hup', '', '', 'Hupa', 'hupa'),
             ('iba', '', '', 'Iban', 'iban'),
             ('ibo', '', 'ig', 'Igbo', 'igbo'),
             ('ice', 'isl', 'is', 'Icelandic', 'islandais'),
             ('ido', '', 'io', 'Ido', 'ido'),
             ('iii', '', 'ii', 'Sichuan Yi; Nuosu', 'yi de Sichuan'),
             ('ijo', '', '', 'Ijo languages', 'ijo, langues'),
             ('iku', '', 'iu', 'Inuktitut', 'inuktitut'),
             ('ile', '', 'ie', 'Interlingue; Occidental', 'interlingue'),
             ('ilo', '', '', 'Iloko', 'ilocano'),
             ('ina', '', 'ia', 'Interlingua (International Auxiliary Language Association)',
              'interlingua (langue auxiliaire internationale)'),
             ('inc', '', '', 'Indic languages', 'indo-aryennes, langues'),
             ('ind', '', 'id', 'Indonesian', 'indonésien'),
             ('ine', '', '', 'Indo-European languages', 'indo-européennes, langues'),
             ('inh', '', '', 'Ingush', 'ingouche'),
             ('ipk', '', 'ik', 'Inupiaq', 'inupiaq'),
             ('ira', '', '', 'Iranian languages', 'iraniennes, langues'),
             ('iro', '', '', 'Iroquoian languages', 'iroquoises, langues'),
             ('ita', '', 'it', 'Italian', 'italien'),
             ('jav', '', 'jv', 'Javanese', 'javanais'),
             ('jbo', '', '', 'Lojban', 'lojban'),
             ('jpn', '', 'ja', 'Japanese', 'japonais'),
             ('jpr', '', '', 'Judeo-Persian', 'judéo-persan'),
             ('jrb', '', '', 'Judeo-Arabic', 'judéo-arabe'),
             ('kaa', '', '', 'Kara-Kalpak', 'karakalpak'),
             ('kab', '', '', 'Kabyle', 'kabyle'),
             ('kac', '', '', 'Kachin; Jingpho', 'kachin; jingpho'),
             ('kal', '', 'kl', 'Kalaallisut; Greenlandic', 'groenlandais'),
             ('kam', '', '', 'Kamba', 'kamba'),
             ('kan', '', 'kn', 'Kannada', 'kannada'),
             ('kar', '', '', 'Karen languages', 'karen, langues'),
             ('kas', '', 'ks', 'Kashmiri', 'kashmiri'),
             ('kau', '', 'kr', 'Kanuri', 'kanouri'),
             ('kaw', '', '', 'Kawi', 'kawi'),
             ('kaz', '', 'kk', 'Kazakh', 'kazakh'),
             ('kbd', '', '', 'Kabardian', 'kabardien'),
             ('kha', '', '', 'Khasi', 'khasi'),
             ('khi', '', '', 'Khoisan languages', 'khoïsan, langues'),
             ('khm', '', 'km', 'Central Khmer', 'khmer central'),
             ('kho', '', '', 'Khotanese; Sakan', 'khotanais; sakan'),
             ('kik', '', 'ki', 'Kikuyu; Gikuyu', 'kikuyu'),
             ('kin', '', 'rw', 'Kinyarwanda', 'rwanda'),
             ('kir', '', 'ky', 'Kirghiz; Kyrgyz', 'kirghiz'),
             ('kmb', '', '', 'Kimbundu', 'kimbundu'),
             ('kok', '', '', 'Konkani', 'konkani'),
             ('kom', '', 'kv', 'Komi', 'kom'),
             ('kon', '', 'kg', 'Kongo', 'kongo'),
             ('kor', '', 'ko', 'Korean', 'coréen'),
             ('kos', '', '', 'Kosraean', 'kosrae'),
             ('kpe', '', '', 'Kpelle', 'kpellé'),
             ('krc', '', '', 'Karachay-Balkar', 'karatchai balkar'),
             ('krl', '', '', 'Karelian', 'carélien'),
             ('kro', '', '', 'Kru languages', 'krou, langues'),
             ('kru', '', '', 'Kurukh', 'kurukh'),
             ('kua', '', 'kj', 'Kuanyama; Kwanyama', 'kuanyama; kwanyama'),
             ('kum', '', '', 'Kumyk', 'koumyk'),
             ('kur', '', 'ku', 'Kurdish', 'kurde'),
             ('kut', '', '', 'Kutenai', 'kutenai'),
             ('lad', '', '', 'Ladino', 'judéo-espagnol'),
             ('lah', '', '', 'Lahnda', 'lahnda'),
             ('lam', '', '', 'Lamba', 'lamba'),
             ('lao', '', 'lo', 'Lao', 'lao'),
             ('lat', '', 'la', 'Latin', 'latin'),
             ('lav', '', 'lv', 'Latvian', 'letton'),
             ('lez', '', '', 'Lezghian', 'lezghien'),
             ('lim', '', 'li', 'Limburgan; Limburger; Limburgish', 'limbourgeois'),
             ('lin', '', 'ln', 'Lingala', 'lingala'),
             ('lit', '', 'lt', 'Lithuanian', 'lituanien'),
             ('lol', '', '', 'Mongo', 'mongo'),
             ('loz', '', '', 'Lozi', 'lozi'),
             ('ltz', '', 'lb', 'Luxembourgish; Letzeburgesch', 'luxembourgeois'),
             ('lua', '', '', 'Luba-Lulua', 'luba-lulua'),
             ('lub', '', 'lu', 'Luba-Katanga', 'luba-katanga'),
             ('lug', '', 'lg', 'Ganda', 'ganda'),
             ('lui', '', '', 'Luiseno', 'luiseno'),
             ('lun', '', '', 'Lunda', 'lunda'),
             ('luo', '', '', 'Luo (Kenya and Tanzania)', 'luo (Kenya et Tanzanie)'),
             ('lus', '', '', 'Lushai', 'lushai'),
             ('mac', 'mkd', 'mk', 'Macedonian', 'macédonien'),
             ('mad', '', '', 'Madurese', 'madourais'),
             ('mag', '', '', 'Magahi', 'magahi'),
             ('mah', '', 'mh', 'Marshallese', 'marshall'),
             ('mai', '', '', 'Maithili', 'maithili'),
             ('mak', '', '', 'Makasar', 'makassar'),
             ('mal', '', 'ml', 'Malayalam', 'malayalam'),
             ('man', '', '', 'Mandingo', 'mandingue'),
             ('mao', 'mri', 'mi', 'Maori', 'maori'),
             ('map', '', '', 'Austronesian languages', 'austronésiennes, langues'),
             ('mar', '', 'mr', 'Marathi', 'marathe'),
             ('mas', '', '', 'Masai', 'massaï'),
             ('may', 'msa', 'ms', 'Malay', 'malais'),
             ('mdf', '', '', 'Moksha', 'moksa'),
             ('mdr', '', '', 'Mandar', 'mandar'),
             ('men', '', '', 'Mende', 'mendé'),
             ('mga', '', '', 'Irish, Middle (900-1200)', 'irlandais moyen (900-1200)'),
             ('mic', '', '', 'Mi\'kmaq; Micmac', 'mi\'kmaq; micmac'),
             ('min', '', '', 'Minangkabau', 'minangkabau'),
             ('mkh', '', '', 'Mon-Khmer languages', 'môn-khmer, langues'),
             ('mlg', '', 'mg', 'Malagasy', 'malgache'),
             ('mlt', '', 'mt', 'Maltese', 'maltais'),
             ('mnc', '', '', 'Manchu', 'mandchou'),
             ('mni', '', '', 'Manipuri', 'manipuri'),
             ('mno', '', '', 'Manobo languages', 'manobo, langues'),
             ('moh', '', '', 'Mohawk', 'mohawk'),
             ('mon', '', 'mn', 'Mongolian', 'mongol'),
             ('mos', '', '', 'Mossi', 'moré'),
             ('mun', '', '', 'Munda languages', 'mounda, langues'),
             ('mus', '', '', 'Creek', 'muskogee'),
             ('mwl', '', '', 'Mirandese', 'mirandais'),
             ('mwr', '', '', 'Marwari', 'marvari'),
             ('myn', '', '', 'Mayan languages', 'maya, langues'),
             ('myv', '', '', 'Erzya', 'erza'),
             ('nah', '', '', 'Nahuatl languages', 'nahuatl, langues'),
             ('nai', '', '', 'North American Indian languages', 'nord-amérindiennes, langues'),
             ('nap', '', '', 'Neapolitan', 'napolitain'),
             ('nau', '', 'na', 'Nauru', 'nauruan'),
             ('nav', '', 'nv', 'Navajo; Navaho', 'navaho'),
             ('nbl', '', 'nr', 'Ndebele, South; South Ndebele', 'ndébélé du Sud'),
             ('nde', '', 'nd', 'Ndebele, North; North Ndebele', 'ndébélé du Nord'),
             ('ndo', '', 'ng', 'Ndonga', 'ndonga'),
             ('nds', '', '', 'Low German; Low Saxon; German, Low; Saxon, Low',
              'bas allemand; bas saxon; allemand, bas; saxon, bas'),
             ('nep', '', 'ne', 'Nepali', 'népalais'),
             ('new', '', '', 'Nepal Bhasa; Newari', 'nepal bhasa; newari'),
             ('nia', '', '', 'Nias', 'nias'),
             ('nic', '', '', 'Niger-Kordofanian languages', 'nigéro-kordofaniennes, langues'),
             ('niu', '', '', 'Niuean', 'niué'),
             ('nno', '', 'nn', 'Norwegian Nynorsk; Nynorsk, Norwegian', 'norvégien nynorsk; nynorsk, norvégien'),
             ('nob', '', 'nb', 'Bokmål, Norwegian; Norwegian Bokmål', 'norvégien bokmål'),
             ('nog', '', '', 'Nogai', 'nogaï; nogay'),
             ('non', '', '', 'Norse, Old', 'norrois, vieux'),
             ('nor', '', 'no', 'Norwegian', 'norvégien'),
             ('nqo', '', '', 'N\'Ko', 'n\'ko'),
             ('nso', '', '', 'Pedi; Sepedi; Northern Sotho', 'pedi; sepedi; sotho du Nord'),
             ('nub', '', '', 'Nubian languages', 'nubiennes, langues'),
             ('nwc', '', '', 'Classical Newari; Old Newari; Classical Nepal Bhasa', 'newari classique'),
             ('nya', '', 'ny', 'Chichewa; Chewa; Nyanja', 'chichewa; chewa; nyanja'),
             ('nym', '', '', 'Nyamwezi', 'nyamwezi'),
             ('nyn', '', '', 'Nyankole', 'nyankolé'),
             ('nyo', '', '', 'Nyoro', 'nyoro'),
             ('nzi', '', '', 'Nzima', 'nzema'),
             ('oci', '', 'oc', 'Occitan (post 1500); Provençal', 'occitan (après 1500); provençal'),
             ('oji', '', 'oj', 'Ojibwa', 'ojibwa'),
             ('ori', '', 'or', 'Oriya', 'oriya'),
             ('orm', '', 'om', 'Oromo', 'galla'),
             ('osa', '', '', 'Osage', 'osage'),
             ('oss', '', 'os', 'Ossetian; Ossetic', 'ossète'),
             ('ota', '', '', 'Turkish, Ottoman (1500-1928)', 'turc ottoman (1500-1928)'),
             ('oto', '', '', 'Otomian languages', 'otomi, langues'),
             ('paa', '', '', 'Papuan languages', 'papoues, langues'),
             ('pag', '', '', 'Pangasinan', 'pangasinan'),
             ('pal', '', '', 'Pahlavi', 'pahlavi'),
             ('pam', '', '', 'Pampanga; Kapampangan', 'pampangan'),
             ('pan', '', 'pa', 'Panjabi; Punjabi', 'pendjabi'),
             ('pap', '', '', 'Papiamento', 'papiamento'),
             ('pau', '', '', 'Palauan', 'palau'),
             ('peo', '', '', 'Persian, Old (ca.600-400 B.C.)', 'perse, vieux (ca. 600-400 av. J.-C.)'),
             ('per', 'fas', 'fa', 'Persian', 'persan'),
             ('phi', '', '', 'Philippine languages', 'philippines, langues'),
             ('phn', '', '', 'Phoenician', 'phénicien'),
             ('pli', '', 'pi', 'Pali', 'pali'),
             ('pol', '', 'pl', 'Polish', 'polonais'),
             ('pon', '', '', 'Pohnpeian', 'pohnpei'),
             ('por', '', 'pt', 'Portuguese', 'portugais'),
             ('pra', '', '', 'Prakrit languages', 'prâkrit, langues'),
             ('pro', '', '', 'Provençal, Old (to 1500)', 'provençal ancien (jusqu\'à 1500)'),
             ('pus', '', 'ps', 'Pushto; Pashto', 'pachto'),
             ('que', '', 'qu', 'Quechua', 'quechua'),
             ('raj', '', '', 'Rajasthani', 'rajasthani'),
             ('rap', '', '', 'Rapanui', 'rapanui'),
             ('rar', '', '', 'Rarotongan; Cook Islands Maori', 'rarotonga; maori des îles Cook'),
             ('roa', '', '', 'Romance languages', 'romanes, langues'),
             ('roh', '', 'rm', 'Romansh', 'romanche'),
             ('rom', '', '', 'Romany', 'tsigane'),
             ('rum', 'ron', 'ro', 'Romanian; Moldavian; Moldovan', 'roumain; moldave'),
             ('run', '', 'rn', 'Rundi', 'rundi'),
             ('rup', '', '', 'Aromanian; Arumanian; Macedo-Romanian', 'aroumain; macédo-roumain'),
             ('rus', '', 'ru', 'Russian', 'russe'),
             ('sad', '', '', 'Sandawe', 'sandawe'),
             ('sag', '', 'sg', 'Sango', 'sango'),
             ('sah', '', '', 'Yakut', 'iakoute'),
             ('sai', '', '', 'South American Indian (Other)', 'indiennes d\'Amérique du Sud, autres langues'),
             ('sal', '', '', 'Salishan languages', 'salishennes, langues'),
             ('sam', '', '', 'Samaritan Aramaic', 'samaritain'),
             ('san', '', 'sa', 'Sanskrit', 'sanskrit'),
             ('sas', '', '', 'Sasak', 'sasak'),
             ('sat', '', '', 'Santali', 'santal'),
             ('scn', '', '', 'Sicilian', 'sicilien'),
             ('sco', '', '', 'Scots', 'écossais'),
             ('sel', '', '', 'Selkup', 'selkoupe'),
             ('sem', '', '', 'Semitic languages', 'sémitiques, langues'),
             ('sga', '', '', 'Irish, Old (to 900)', 'irlandais ancien (jusqu\'à 900)'),
             ('sgn', '', '', 'Sign Languages', 'langues des signes'),
             ('shn', '', '', 'Shan', 'chan'),
             ('sid', '', '', 'Sidamo', 'sidamo'),
             ('sin', '', 'si', 'Sinhala; Sinhalese', 'singhalais'),
             ('sio', '', '', 'Siouan languages', 'sioux, langues'),
             ('sit', '', '', 'Sino-Tibetan languages', 'sino-tibétaines, langues'),
             ('sla', '', '', 'Slavic languages', 'slaves, langues'),
             ('slo', 'slk', 'sk', 'Slovak', 'slovaque'),
             ('slv', '', 'sl', 'Slovenian', 'slovène'),
             ('sma', '', '', 'Southern Sami', 'sami du Sud'),
             ('sme', '', 'se', 'Northern Sami', 'sami du Nord'),
             ('smi', '', '', 'Sami languages', 'sames, langues'),
             ('smj', '', '', 'Lule Sami', 'sami de Lule'),
             ('smn', '', '', 'Inari Sami', 'sami d\'Inari'),
             ('smo', '', 'sm', 'Samoan', 'samoan'),
             ('sms', '', '', 'Skolt Sami', 'sami skolt'),
             ('sna', '', 'sn', 'Shona', 'shona'),
             ('snd', '', 'sd', 'Sindhi', 'sindhi'),
             ('snk', '', '', 'Soninke', 'soninké'),
             ('sog', '', '', 'Sogdian', 'sogdien'),
             ('som', '', 'so', 'Somali', 'somali'),
             ('son', '', '', 'Songhai languages', 'songhai, langues'),
             ('sot', '', 'st', 'Sotho, Southern', 'sotho du Sud'),
             ('spa', '', 'es', 'Spanish; Castilian', 'espagnol; castillan'),
             ('srd', '', 'sc', 'Sardinian', 'sarde'),
             ('srn', '', '', 'Sranan Tongo', 'sranan tongo'),
             ('srp', '', 'sr', 'Serbian', 'serbe'),
             ('srr', '', '', 'Serer', 'sérère'),
             ('ssa', '', '', 'Nilo-Saharan languages', 'nilo-sahariennes, langues'),
             ('ssw', '', 'ss', 'Swati', 'swati'),
             ('suk', '', '', 'Sukuma', 'sukuma'),
             ('sun', '', 'su', 'Sundanese', 'soundanais'),
             ('sus', '', '', 'Susu', 'soussou'),
             ('sux', '', '', 'Sumerian', 'sumérien'),
             ('swa', '', 'sw', 'Swahili', 'swahili'),
             ('swe', '', 'sv', 'Swedish', 'suédois'),
             ('syc', '', '', 'Classical Syriac', 'syriaque classique'),
             ('syr', '', '', 'Syriac', 'syriaque'),
             ('tah', '', 'ty', 'Tahitian', 'tahitien'),
             ('tai', '', '', 'Tai languages', 'tai, langues'),
             ('tam', '', 'ta', 'Tamil', 'tamoul'),
             ('tat', '', 'tt', 'Tatar', 'tatar'),
             ('tel', '', 'te', 'Telugu', 'télougou'),
             ('tem', '', '', 'Timne', 'temne'),
             ('ter', '', '', 'Tereno', 'tereno'),
             ('tet', '', '', 'Tetum', 'tetum'),
             ('tgk', '', 'tg', 'Tajik', 'tadjik'),
             ('tgl', '', 'tl', 'Tagalog', 'tagalog'),
             ('tha', '', 'th', 'Thai', 'thaï'),
             ('tib', 'bod', 'bo', 'Tibetan', 'tibétain'),
             ('tig', '', '', 'Tigre', 'tigré'),
             ('tir', '', 'ti', 'Tigrinya', 'tigrigna'),
             ('tiv', '', '', 'Tiv', 'tiv'),
             ('tkl', '', '', 'Tokelau', 'tokelau'),
             ('tlh', '', '', 'Klingon; tlhIngan-Hol', 'klingon'),
             ('tli', '', '', 'Tlingit', 'tlingit'),
             ('tmh', '', '', 'Tamashek', 'tamacheq'),
             ('tog', '', '', 'Tonga (Nyasa)', 'tonga (Nyasa)'),
             ('ton', '', 'to', 'Tonga (Tonga Islands)', 'tongan (Îles Tonga)'),
             ('tpi', '', '', 'Tok Pisin', 'tok pisin'),
             ('tsi', '', '', 'Tsimshian', 'tsimshian'),
             ('tsn', '', 'tn', 'Tswana', 'tswana'),
             ('tso', '', 'ts', 'Tsonga', 'tsonga'),
             ('tuk', '', 'tk', 'Turkmen', 'turkmène'),
             ('tum', '', '', 'Tumbuka', 'tumbuka'),
             ('tup', '', '', 'Tupi languages', 'tupi, langues'),
             ('tur', '', 'tr', 'Turkish', 'turc'),
             ('tut', '', '', 'Altaic languages', 'altaïques, langues'),
             ('tvl', '', '', 'Tuvalu', 'tuvalu'),
             ('twi', '', 'tw', 'Twi', 'twi'),
             ('tyv', '', '', 'Tuvinian', 'touva'),
             ('udm', '', '', 'Udmurt', 'oudmourte'),
             ('uga', '', '', 'Ugaritic', 'ougaritique'),
             ('uig', '', 'ug', 'Uighur; Uyghur', 'ouïgour'),
             ('ukr', '', 'uk', 'Ukrainian', 'ukrainien'),
             ('umb', '', '', 'Umbundu', 'umbundu'),
             ('und', '', '', 'Undetermined', 'indéterminée'),
             ('urd', '', 'ur', 'Urdu', 'ourdou'),
             ('uzb', '', 'uz', 'Uzbek', 'ouszbek'),
             ('vai', '', '', 'Vai', 'vaï'),
             ('ven', '', 've', 'Venda', 'venda'),
             ('vie', '', 'vi', 'Vietnamese', 'vietnamien'),
             ('vol', '', 'vo', 'Volapük', 'volapük'),
             ('vot', '', '', 'Votic', 'vote'),
             ('wak', '', '', 'Wakashan languages', 'wakashanes, langues'),
             ('wal', '', '', 'Walamo', 'walamo'),
             ('war', '', '', 'Waray', 'waray'),
             ('was', '', '', 'Washo', 'washo'),
             ('wel', 'cym', 'cy', 'Welsh', 'gallois'),
             ('wen', '', '', 'Sorbian languages', 'sorabes, langues'),
             ('wln', '', 'wa', 'Walloon', 'wallon'),
             ('wol', '', 'wo', 'Wolof', 'wolof'),
             ('xal', '', '', 'Kalmyk; Oirat', 'kalmouk; oïrat'),
             ('xho', '', 'xh', 'Xhosa', 'xhosa'),
             ('yao', '', '', 'Yao', 'yao'),
             ('yap', '', '', 'Yapese', 'yapois'),
             ('yid', '', 'yi', 'Yiddish', 'yiddish'),
             ('yor', '', 'yo', 'Yoruba', 'yoruba'),
             ('ypk', '', '', 'Yupik languages', 'yupik, langues'),
             ('zap', '', '', 'Zapotec', 'zapotèque'),
             ('zbl', '', '', 'Blissymbols; Blissymbolics; Bliss', 'symboles Bliss; Bliss'),
             ('zen', '', '', 'Zenaga', 'zenaga'),
             ('zha', '', 'za', 'Zhuang; Chuang', 'zhuang; chuang'),
             ('znd', '', '', 'Zande languages', 'zandé, langues'),
             ('zul', '', 'zu', 'Zulu', 'zoulou'),
             ('zun', '', '', 'Zuni', 'zuni'),
             ('zza', '', '', 'Zaza; Dimili; Dimli; Kirdki; Kirmanjki; Zazaki',
              'zaza; dimili; dimli; kirdki; kirmanjki; zazaki')]


class Country(object):
    """Country according to ISO-3166

    :param string country: country name, alpha2 code, alpha3 code or numeric code
    :param list countries: all countries
    :type countries: see :data:`~subliminal.language.COUNTRIES`

    """
    def __init__(self, country, countries=None):
        countries = countries or COUNTRIES
        country = to_unicode(country.strip().lower())
        country_tuple = None

        # Try to find the country
        if len(country) == 2:
            country_tuple = dict((c[0].lower(), c) for c in countries).get(country)
        elif len(country) == 3 and not country.isdigit():
            country_tuple = dict((c[1].lower(), c) for c in countries).get(country)
        elif len(country) == 3 and country.isdigit():
            country_tuple = dict((c[2].lower(), c) for c in countries).get(country)
        if country_tuple is None:
            country_tuple = dict((c[3].lower(), c) for c in countries).get(country)

        # Raise ValueError if nothing is found
        if country_tuple is None:
            raise ValueError('Country %s does not exist' % country)

        # Set default attrs
        self.alpha2 = country_tuple[0]
        self.alpha3 = country_tuple[1]
        self.numeric = country_tuple[2]
        self.name = country_tuple[3]

    def __hash__(self):
        return hash(self.alpha3)

    def __eq__(self, other):
        if isinstance(other, Country):
            return self.alpha3 == other.alpha3
        return False

    def __ne__(self, other):
        return not self == other

    def __unicode__(self):
        return self.name

    def __str__(self):
        return str(self).encode('utf-8')

    def __repr__(self):
        return 'Country(%s)' % self


class Language(object):
    """Language according to ISO-639

    :param string language: language name (english or french), alpha2 code, alpha3 code, terminologic code or numeric code, eventually with a country
    :param country: country of the language
    :type country: :class:`Country` or string
    :param languages: all languages
    :type languages: see :data:`~subliminal.language.LANGUAGES`
    :param countries: all countries
    :type countries: see :data:`~subliminal.language.COUNTRIES`
    :param bool strict: whether to raise a ValueError on unknown language or not

    :class:`Language` implements the inclusion test, with the ``in`` keyword::

        >>> Language('pt-BR') in Language('pt')  # Portuguese (Brazil) is included in Portuguese
        True
        >>> Language('pt') in Language('pt-BR')  # Portuguese is not included in Portuguese (Brazil)
        False

    """
    with_country_regexps = [re.compile('(.*)\((.*)\)'), re.compile('(.*)[-_](.*)')]

    def __init__(self, language, country=None, languages=None, countries=None, strict=True):
        languages = languages or LANGUAGES
        countries = countries or COUNTRIES

        # Get the country
        self.country = None
        if isinstance(country, Country):
            self.country = country
        elif isinstance(country, str):
            try:
                self.country = Country(country, countries)
            except ValueError:
                logger.warning('Country %s could not be identified' % country)
                if strict:
                    raise

        # Language + Country format
        #TODO: Improve this part
        if country is None:
            for regexp in [r.match(language) for r in self.with_country_regexps]:
                if regexp:
                    language = regexp.group(1)
                    try:
                        self.country = Country(regexp.group(2), countries)
                    except ValueError:
                        logger.warning('Country %s could not be identified' % country)
                        if strict:
                            raise
                    break

        # Try to find the language
        language = to_unicode(language.strip().lower())
        language_tuple = None
        if len(language) == 2:
            language_tuple = dict((l[2].lower(), l) for l in languages).get(language)
        elif len(language) == 3:
            language_tuple = dict((l[0].lower(), l) for l in languages).get(language)
            if language_tuple is None:
                language_tuple = dict((l[1].lower(), l) for l in languages).get(language)
        if language_tuple is None:
            language_tuple = dict((l[3].split('; ')[0].lower(), l) for l in languages).get(language)
        if language_tuple is None:
            language_tuple = dict((l[4].split('; ')[0].lower(), l) for l in languages).get(language)

        # Raise ValueError if strict or continue with Undetermined
        if language_tuple is None:
            if strict:
                raise ValueError('Language %s does not exist' % language)
            language_tuple = dict((l[0].lower(), l) for l in languages).get('und')

        # Set attributes
        self.alpha2 = language_tuple[2]
        self.alpha3 = language_tuple[0]
        self.terminologic = language_tuple[1]
        self.name = language_tuple[3]
        self.french_name = language_tuple[4]

    def __hash__(self):
        if self.country is None:
            return hash(self.alpha3)
        return hash(self.alpha3 + self.country.alpha3)

    def __eq__(self, other):
        if isinstance(other, Language):
            return self.alpha3 == other.alpha3 and self.country == other.country
        return False

    def __contains__(self, item):
        if isinstance(item, Language):
            if self == item:
                return True
            if self.country is None:
                return self.alpha3 == item.alpha3
        return False

    def __ne__(self, other):
        return not self == other

    def __bool__(self):
        return self.alpha3 != 'und'

    def __unicode__(self):
        if self.country is None:
            return self.name
        return '%s (%s)' % (self.name, self.country)

    def __str__(self):
        return str(self).encode('utf-8')

    def __repr__(self):
        if self.country is None:
            return 'Language(%s)' % self.name.encode('utf-8')
        return 'Language(%s, country=%s)' % (self.name.encode('utf-8'), self.country)


class language_set(set):
    """Set of :class:`Language` with some specificities.

    :param iterable: where to take elements from
    :type iterable: iterable of :class:`Languages <Language>` or string
    :param languages: all languages
    :type languages: see :data:`~subliminal.language.LANGUAGES`
    :param bool strict: whether to raise a ValueError on invalid language or not

    The following redefinitions are meant to reflect the inclusion logic in :class:`Language`

    * Inclusion test, with the ``in`` keyword
    * Intersection
    * Substraction

    Here is an illustration of the previous points::

        >>> Language('en') in language_set(['en-US', 'en-CA'])
        False
        >>> Language('en-US') in language_set(['en', 'fr'])
        True
        >>> language_set(['en']) & language_set(['en-US', 'en-CA'])
        language_set([Language(English, country=Canada), Language(English, country=United States)])
        >>> language_set(['en-US', 'en-CA', 'fr']) - language_set(['en'])
        language_set([Language(French)])

    """
    def __init__(self, iterable=None, languages=None, strict=True):
        iterable = iterable or []
        languages = languages or LANGUAGES
        items = []
        for i in iterable:
            if isinstance(i, Language):
                items.append(i)
                continue
            if isinstance(i, tuple):
                items.append(Language(i[0], languages=languages, strict=strict))
                continue
            items.append(Language(i, languages=languages, strict=strict))
        super(language_set, self).__init__(items)

    def __contains__(self, item):
        for i in self:
            if item in i:
                return True
        return super(language_set, self).__contains__(item)

    def __and__(self, other):
        results = language_set()
        for i in self:
            for j in other:
                if i in j:
                    results.add(i)
        for i in other:
            for j in self:
                if i in j:
                    results.add(i)
        return results

    def __sub__(self, other):
        results = language_set()
        for i in self:
            if i not in other:
                results.add(i)
        return results


class language_list(list):
    """List of :class:`Language` with some specificities.

    :param iterable: where to take elements from
    :type iterable: iterable of :class:`Languages <Language>` or string
    :param languages: all languages
    :type languages: see :data:`~subliminal.language.LANGUAGES`
    :param bool strict: whether to raise a ValueError on invalid language or not

    The following redefinitions are meant to reflect the inclusion logic in :class:`Language`

    * Inclusion test, with the ``in`` keyword
    * Index

    Here is an illustration of the previous points::

        >>> Language('en') in language_list(['en-US', 'en-CA'])
        False
        >>> Language('en-US') in language_list(['en', 'fr-BE'])
        True
        >>> language_list(['en', 'fr-BE']).index(Language('en-US'))
        0

    """
    def __init__(self, iterable=None, languages=None, strict=True):
        iterable = iterable or []
        languages = languages or LANGUAGES
        items = []
        for i in iterable:
            if isinstance(i, Language):
                items.append(i)
                continue
            if isinstance(i, tuple):
                items.append(Language(i[0], languages=languages, strict=strict))
                continue
            items.append(Language(i, languages=languages, strict=strict))
        super(language_list, self).__init__(items)

    def __contains__(self, item):
        for i in self:
            if item in i:
                return True
        return super(language_list, self).__contains__(item)

    def index(self, x, strict=False):
        if not strict:
            for i in range(len(self)):
                if x in self[i]:
                    return i
        return super(language_list, self).index(x)
