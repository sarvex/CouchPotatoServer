# -*- coding: utf-8 -*-
# enzyme - Video metadata parser
# Copyright 2011-2012 Antoine Bertin <diaoulael@gmail.com>
# Copyright 2003-2006 Dirk Meyer <dischi@freevo.org>
#
# This file is part of enzyme.
#
# enzyme is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# enzyme is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with enzyme.  If not, see <http://www.gnu.org/licenses/>.
import re
import string
import struct

__all__ = ['resolve']


def resolve(code):
    """
    Transform a twocc or fourcc code into a name.  Returns a 2-tuple of (cc,
    codec) where both are strings and cc is a string in the form '0xXX' if it's
    a twocc, or 'ABCD' if it's a fourcc.  If the given code is not a known
    twocc or fourcc, the return value will be (None, 'Unknown'), unless the
    code is otherwise a printable string in which case it will be returned as
    the codec.
    """
    if isinstance(code, str):
        codec = 'Unknown'
        # Check for twocc
        if re.match(r'^0x[\da-f]{1,4}$', code, re.I):
            # Twocc in hex form
            return code, TWOCC.get(int(code, 16), codec)
        elif code.isdigit() and 0 <= int(code) <= 0xff:
            # Twocc in decimal form
            return hex(int(code)), TWOCC.get(int(code), codec)
        elif len(code) == 2:
            code = struct.unpack('H', code)[0]
            return hex(code), TWOCC.get(code, codec)
        elif len(code) != 4 and len([x for x in code if x not in string.printable]) == 0:
            # Code is a printable string.
            codec = str(code)

        if code[:2] == 'MS' and code[2:].upper() in FOURCC:
            code = code[2:]

        if code.upper() in FOURCC:
            return code.upper(), str(FOURCC[code.upper()])
        return None, codec
    elif isinstance(code, int):
        return hex(code), TWOCC.get(code, 'Unknown')

    return None, 'Unknown'


TWOCC = {
    0x0000: 'Unknown Wave Format',
    0x0001: 'PCM',
    0x0002: 'Microsoft ADPCM',
    0x0003: 'IEEE Float',
    0x0004: 'Compaq Computer VSELP',
    0x0005: 'IBM CVSD',
    0x0006: 'A-Law',
    0x0007: 'mu-Law',
    0x0008: 'Microsoft DTS',
    0x0009: 'Microsoft DRM',
    0x0010: 'OKI ADPCM',
    0x0011: 'Intel DVI/IMA ADPCM',
    0x0012: 'Videologic MediaSpace ADPCM',
    0x0013: 'Sierra Semiconductor ADPCM',
    0x0014: 'Antex Electronics G.723 ADPCM',
    0x0015: 'DSP Solutions DigiSTD',
    0x0016: 'DSP Solutions DigiFIX',
    0x0017: 'Dialogic OKI ADPCM',
    0x0018: 'MediaVision ADPCM',
    0x0019: 'Hewlett-Packard CU',
    0x0020: 'Yamaha ADPCM',
    0x0021: 'Speech Compression Sonarc',
    0x0022: 'DSP Group TrueSpeech',
    0x0023: 'Echo Speech EchoSC1',
    0x0024: 'Audiofile AF36',
    0x0025: 'Audio Processing Technology APTX',
    0x0026: 'AudioFile AF10',
    0x0027: 'Prosody 1612',
    0x0028: 'LRC',
    0x0030: 'Dolby AC2',
    0x0031: 'Microsoft GSM 6.10',
    0x0032: 'MSNAudio',
    0x0033: 'Antex Electronics ADPCME',
    0x0034: 'Control Resources VQLPC',
    0x0035: 'DSP Solutions DigiREAL',
    0x0036: 'DSP Solutions DigiADPCM',
    0x0037: 'Control Resources CR10',
    0x0038: 'Natural MicroSystems VBXADPCM',
    0x0039: 'Crystal Semiconductor IMA ADPCM',
    0x003A: 'EchoSC3',
    0x003B: 'Rockwell ADPCM',
    0x003C: 'Rockwell Digit LK',
    0x003D: 'Xebec',
    0x0040: 'Antex Electronics G.721 ADPCM',
    0x0041: 'G.728 CELP',
    0x0042: 'MSG723',
    0x0043: 'IBM AVC ADPCM',
    0x0045: 'ITU-T G.726 ADPCM',
    0x0050: 'MPEG 1, Layer 1,2',
    0x0052: 'RT24',
    0x0053: 'PAC',
    0x0055: 'MPEG Layer 3',
    0x0059: 'Lucent G.723',
    0x0060: 'Cirrus',
    0x0061: 'ESPCM',
    0x0062: 'Voxware',
    0x0063: 'Canopus Atrac',
    0x0064: 'G.726 ADPCM',
    0x0065: 'G.722 ADPCM',
    0x0066: 'DSAT',
    0x0067: 'DSAT Display',
    0x0069: 'Voxware Byte Aligned',
    0x0070: 'Voxware AC8',
    0x0071: 'Voxware AC10',
    0x0072: 'Voxware AC16',
    0x0073: 'Voxware AC20',
    0x0074: 'Voxware MetaVoice',
    0x0075: 'Voxware MetaSound',
    0x0076: 'Voxware RT29HW',
    0x0077: 'Voxware VR12',
    0x0078: 'Voxware VR18',
    0x0079: 'Voxware TQ40',
    0x0080: 'Softsound',
    0x0081: 'Voxware TQ60',
    0x0082: 'MSRT24',
    0x0083: 'G.729A',
    0x0084: 'MVI MV12',
    0x0085: 'DF G.726',
    0x0086: 'DF GSM610',
    0x0088: 'ISIAudio',
    0x0089: 'Onlive',
    0x0091: 'SBC24',
    0x0092: 'Dolby AC3 SPDIF',
    0x0093: 'MediaSonic G.723',
    0x0094: 'Aculab PLC Prosody 8KBPS',
    0x0097: 'ZyXEL ADPCM',
    0x0098: 'Philips LPCBB',
    0x0099: 'Packed',
    0x00A0: 'Malden Electronics PHONYTALK',
    0x00FF: 'AAC',
    0x0100: 'Rhetorex ADPCM',
    0x0101: 'IBM mu-law',
    0x0102: 'IBM A-law',
    0x0103: 'IBM AVC Adaptive Differential Pulse Code Modulation',
    0x0111: 'Vivo G.723',
    0x0112: 'Vivo Siren',
    0x0123: 'Digital G.723',
    0x0125: 'Sanyo LD ADPCM',
    0x0130: 'Sipro Lab Telecom ACELP.net',
    0x0131: 'Sipro Lab Telecom ACELP.4800',
    0x0132: 'Sipro Lab Telecom ACELP.8V3',
    0x0133: 'Sipro Lab Telecom ACELP.G.729',
    0x0134: 'Sipro Lab Telecom ACELP.G.729A',
    0x0135: 'Sipro Lab Telecom ACELP.KELVIN',
    0x0140: 'Windows Media Video V8',
    0x0150: 'Qualcomm PureVoice',
    0x0151: 'Qualcomm HalfRate',
    0x0155: 'Ring Zero Systems TUB GSM',
    0x0160: 'Windows Media Audio V1 / DivX audio (WMA)',
    0x0161: 'Windows Media Audio V7 / V8 / V9',
    0x0162: 'Windows Media Audio Professional V9',
    0x0163: 'Windows Media Audio Lossless V9',
    0x0170: 'UNISYS NAP ADPCM',
    0x0171: 'UNISYS NAP ULAW',
    0x0172: 'UNISYS NAP ALAW',
    0x0173: 'UNISYS NAP 16K',
    0x0200: 'Creative Labs ADPCM',
    0x0202: 'Creative Labs Fastspeech8',
    0x0203: 'Creative Labs Fastspeech10',
    0x0210: 'UHER Informatic ADPCM',
    0x0215: 'Ulead DV ACM',
    0x0216: 'Ulead DV ACM',
    0x0220: 'Quarterdeck',
    0x0230: 'I-link Worldwide ILINK VC',
    0x0240: 'Aureal Semiconductor RAW SPORT',
    0x0241: 'ESST AC3',
    0x0250: 'Interactive Products HSX',
    0x0251: 'Interactive Products RPELP',
    0x0260: 'Consistent Software CS2',
    0x0270: 'Sony ATRAC3 (SCX, same as MiniDisk LP2)',
    0x0300: 'Fujitsu FM Towns Snd',
    0x0400: 'BTV Digital',
    0x0401: 'Intel Music Coder (IMC)',
    0x0402: 'Ligos Indeo Audio',
    0x0450: 'QDesign Music',
    0x0680: 'VME VMPCM',
    0x0681: 'AT&T Labs TPC',
    0x0700: 'YMPEG Alpha',
    0x08AE: 'ClearJump LiteWave',
    0x1000: 'Olivetti GSM',
    0x1001: 'Olivetti ADPCM',
    0x1002: 'Olivetti CELP',
    0x1003: 'Olivetti SBC',
    0x1004: 'Olivetti OPR',
    0x1100: 'Lernout & Hauspie LH Codec',
    0x1101: 'Lernout & Hauspie CELP codec',
    0x1102: 'Lernout & Hauspie SBC codec',
    0x1103: 'Lernout & Hauspie SBC codec',
    0x1104: 'Lernout & Hauspie SBC codec',
    0x1400: 'Norris',
    0x1401: 'AT&T ISIAudio',
    0x1500: 'Soundspace Music Compression',
    0x181C: 'VoxWare RT24 speech codec',
    0x181E: 'Lucent elemedia AX24000P Music codec',
    0x1C07: 'Lucent SX8300P speech codec',
    0x1C0C: 'Lucent SX5363S G.723 compliant codec',
    0x1F03: 'CUseeMe DigiTalk (ex-Rocwell)',
    0x1FC4: 'NCT Soft ALF2CD ACM',
    0x2000: 'AC3',
    0x2001: 'Dolby DTS (Digital Theater System)',
    0x2002: 'RealAudio 1 / 2 14.4',
    0x2003: 'RealAudio 1 / 2 28.8',
    0x2004: 'RealAudio G2 / 8 Cook (low bitrate)',
    0x2005: 'RealAudio 3 / 4 / 5 Music (DNET)',
    0x2006: 'RealAudio 10 AAC (RAAC)',
    0x2007: 'RealAudio 10 AAC+ (RACP)',
    0x3313: 'makeAVIS',
    0x4143: 'Divio MPEG-4 AAC audio',
    0x434C: 'LEAD Speech',
    0x564C: 'LEAD Vorbis',
    0x674F: 'Ogg Vorbis (mode 1)',
    0x6750: 'Ogg Vorbis (mode 2)',
    0x6751: 'Ogg Vorbis (mode 3)',
    0x676F: 'Ogg Vorbis (mode 1+)',
    0x6770: 'Ogg Vorbis (mode 2+)',
    0x6771: 'Ogg Vorbis (mode 3+)',
    0x7A21: 'GSM-AMR (CBR, no SID)',
    0x7A22: 'GSM-AMR (VBR, including SID)',
    0xDFAC: 'DebugMode SonicFoundry Vegas FrameServer ACM Codec',
    0xF1AC: 'Free Lossless Audio Codec FLAC',
    0xFFFE: 'Extensible wave format',
    0xFFFF: 'development'
}


FOURCC = {
    '1978': 'A.M.Paredes predictor (LossLess)',
    '2VUY': 'Optibase VideoPump 8-bit 4:2:2 Component YCbCr',
    '3IV0': 'MPEG4-based codec 3ivx',
    '3IV1': '3ivx v1',
    '3IV2': '3ivx v2',
    '3IVD': 'FFmpeg DivX ;-) (MS MPEG-4 v3)',
    '3IVX': 'MPEG4-based codec 3ivx',
    '8BPS': 'Apple QuickTime Planar RGB with Alpha-channel',
    'AAS4': 'Autodesk Animator codec (RLE)',
    'AASC': 'Autodesk Animator',
    'ABYR': 'Kensington ABYR',
    'ACTL': 'Streambox ACT-L2',
    'ADV1': 'Loronix WaveCodec',
    'ADVJ': 'Avid M-JPEG Avid Technology Also known as AVRn',
    'AEIK': 'Intel Indeo Video 3.2',
    'AEMI': 'Array VideoONE MPEG1-I Capture',
    'AFLC': 'Autodesk Animator FLC',
    'AFLI': 'Autodesk Animator FLI',
    'AHDV': 'CineForm 10-bit Visually Perfect HD',
    'AJPG': '22fps JPEG-based codec for digital cameras',
    'AMPG': 'Array VideoONE MPEG',
    'ANIM': 'Intel RDX (ANIM)',
    'AP41': 'AngelPotion Definitive',
    'AP42': 'AngelPotion Definitive',
    'ASLC': 'AlparySoft Lossless Codec',
    'ASV1': 'Asus Video v1',
    'ASV2': 'Asus Video v2',
    'ASVX': 'Asus Video 2.0 (audio)',
    'ATM4': 'Ahead Nero Digital MPEG-4 Codec',
    'AUR2': 'Aura 2 Codec - YUV 4:2:2',
    'AURA': 'Aura 1 Codec - YUV 4:1:1',
    'AV1X': 'Avid 1:1x (Quick Time)',
    'AVC1': 'H.264 AVC',
    'AVD1': 'Avid DV (Quick Time)',
    'AVDJ': 'Avid Meridien JFIF with Alpha-channel',
    'AVDN': 'Avid DNxHD (Quick Time)',
    'AVDV': 'Avid DV',
    'AVI1': 'MainConcept Motion JPEG Codec',
    'AVI2': 'MainConcept Motion JPEG Codec',
    'AVID': 'Avid Motion JPEG',
    'AVIS': 'Wrapper for AviSynth',
    'AVMP': 'Avid IMX (Quick Time)',
    'AVR ': 'Avid ABVB/NuVista MJPEG with Alpha-channel',
    'AVRN': 'Avid Motion JPEG',
    'AVUI': 'Avid Meridien Uncompressed with Alpha-channel',
    'AVUP': 'Avid 10bit Packed (Quick Time)',
    'AYUV': '4:4:4 YUV (AYUV)',
    'AZPR': 'Quicktime Apple Video',
    'AZRP': 'Quicktime Apple Video',
    'BGR ': 'Uncompressed BGR32 8:8:8:8',
    'BGR(15)': 'Uncompressed BGR15 5:5:5',
    'BGR(16)': 'Uncompressed BGR16 5:6:5',
    'BGR(24)': 'Uncompressed BGR24 8:8:8',
    'BHIV': 'BeHere iVideo',
    'BINK': 'RAD Game Tools Bink Video',
    'BIT ': 'BI_BITFIELDS (Raw RGB)',
    'BITM': 'Microsoft H.261',
    'BLOX': 'Jan Jezabek BLOX MPEG Codec',
    'BLZ0': 'DivX for Blizzard Decoder Filter',
    'BT20': 'Conexant Prosumer Video',
    'BTCV': 'Conexant Composite Video Codec',
    'BTVC': 'Conexant Composite Video',
    'BW00': 'BergWave (Wavelet)',
    'BW10': 'Data Translation Broadway MPEG Capture',
    'BXBG': 'BOXX BGR',
    'BXRG': 'BOXX RGB',
    'BXY2': 'BOXX 10-bit YUV',
    'BXYV': 'BOXX YUV',
    'CC12': 'Intel YUV12',
    'CDV5': 'Canopus SD50/DVHD',
    'CDVC': 'Canopus DV',
    'CDVH': 'Canopus SD50/DVHD',
    'CFCC': 'Digital Processing Systems DPS Perception',
    'CFHD': 'CineForm 10-bit Visually Perfect HD',
    'CGDI': 'Microsoft Office 97 Camcorder Video',
    'CHAM': 'Winnov Caviara Champagne',
    'CJPG': 'Creative WebCam JPEG',
    'CLJR': 'Cirrus Logic YUV 4 pixels',
    'CLLC': 'Canopus LossLess',
    'CLPL': 'YV12',
    'CMYK': 'Common Data Format in Printing',
    'COL0': 'FFmpeg DivX ;-) (MS MPEG-4 v3)',
    'COL1': 'FFmpeg DivX ;-) (MS MPEG-4 v3)',
    'CPLA': 'Weitek 4:2:0 YUV Planar',
    'CRAM': 'Microsoft Video 1 (CRAM)',
    'CSCD': 'RenderSoft CamStudio lossless Codec',
    'CTRX': 'Citrix Scalable Video Codec',
    'CUVC': 'Canopus HQ',
    'CVID': 'Radius Cinepak',
    'CWLT': 'Microsoft Color WLT DIB',
    'CYUV': 'Creative Labs YUV',
    'CYUY': 'ATI YUV',
    'D261': 'H.261',
    'D263': 'H.263',
    'DAVC': 'Dicas MPEGable H.264/MPEG-4 AVC base profile codec',
    'DC25': 'MainConcept ProDV Codec',
    'DCAP': 'Pinnacle DV25 Codec',
    'DCL1': 'Data Connection Conferencing Codec',
    'DCT0': 'WniWni Codec',
    'DFSC': 'DebugMode FrameServer VFW Codec',
    'DIB ': 'Full Frames (Uncompressed)',
    'DIV1': 'FFmpeg-4 V1 (hacked MS MPEG-4 V1)',
    'DIV2': 'MS MPEG-4 V2',
    'DIV3': 'DivX v3 MPEG-4 Low-Motion',
    'DIV4': 'DivX v3 MPEG-4 Fast-Motion',
    'DIV5': 'DIV5',
    'DIV6': 'DivX MPEG-4',
    'DIVX': 'DivX',
    'DM4V': 'Dicas MPEGable MPEG-4',
    'DMB1': 'Matrox Rainbow Runner hardware MJPEG',
    'DMB2': 'Paradigm MJPEG',
    'DMK2': 'ViewSonic V36 PDA Video',
    'DP02': 'DynaPel MPEG-4',
    'DPS0': 'DPS Reality Motion JPEG',
    'DPSC': 'DPS PAR Motion JPEG',
    'DRWX': 'Pinnacle DV25 Codec',
    'DSVD': 'DSVD',
    'DTMT': 'Media-100 Codec',
    'DTNT': 'Media-100 Codec',
    'DUCK': 'Duck True Motion 1.0',
    'DV10': 'BlueFish444 (lossless RGBA, YUV 10-bit)',
    'DV25': 'Matrox DVCPRO codec',
    'DV50': 'Matrox DVCPRO50 codec',
    'DVAN': 'DVAN',
    'DVC ': 'Apple QuickTime DV (DVCPRO NTSC)',
    'DVCP': 'Apple QuickTime DV (DVCPRO PAL)',
    'DVCS': 'MainConcept DV Codec',
    'DVE2': 'InSoft DVE-2 Videoconferencing',
    'DVH1': 'Pinnacle DVHD100',
    'DVHD': 'DV 1125 lines at 30.00 Hz or 1250 lines at 25.00 Hz',
    'DVIS': 'VSYNC DualMoon Iris DV codec',
    'DVL ': 'Radius SoftDV 16:9 NTSC',
    'DVLP': 'Radius SoftDV 16:9 PAL',
    'DVMA': 'Darim Vision DVMPEG',
    'DVOR': 'BlueFish444 (lossless RGBA, YUV 10-bit)',
    'DVPN': 'Apple QuickTime DV (DV NTSC)',
    'DVPP': 'Apple QuickTime DV (DV PAL)',
    'DVR1': 'TARGA2000 Codec',
    'DVRS': 'VSYNC DualMoon Iris DV codec',
    'DVSD': 'DV',
    'DVSL': 'DV compressed in SD (SDL)',
    'DVX1': 'DVX1000SP Video Decoder',
    'DVX2': 'DVX2000S Video Decoder',
    'DVX3': 'DVX3000S Video Decoder',
    'DX50': 'DivX v5',
    'DXGM': 'Electronic Arts Game Video codec',
    'DXSB': 'DivX Subtitles Codec',
    'DXT1': 'Microsoft DirectX Compressed Texture (DXT1)',
    'DXT2': 'Microsoft DirectX Compressed Texture (DXT2)',
    'DXT3': 'Microsoft DirectX Compressed Texture (DXT3)',
    'DXT4': 'Microsoft DirectX Compressed Texture (DXT4)',
    'DXT5': 'Microsoft DirectX Compressed Texture (DXT5)',
    'DXTC': 'Microsoft DirectX Compressed Texture (DXTC)',
    'DXTN': 'Microsoft DirectX Compressed Texture (DXTn)',
    'EKQ0': 'Elsa EKQ0',
    'ELK0': 'Elsa ELK0',
    'EM2V': 'Etymonix MPEG-2 I-frame',
    'EQK0': 'Elsa graphics card quick codec',
    'ESCP': 'Eidos Escape',
    'ETV1': 'eTreppid Video ETV1',
    'ETV2': 'eTreppid Video ETV2',
    'ETVC': 'eTreppid Video ETVC',
    'FFDS': 'FFDShow supported',
    'FFV1': 'FFDShow supported',
    'FFVH': 'FFVH codec',
    'FLIC': 'Autodesk FLI/FLC Animation',
    'FLJP': 'D-Vision Field Encoded Motion JPEG',
    'FLV1': 'FLV1 codec',
    'FMJP': 'D-Vision fieldbased ISO MJPEG',
    'FRLE': 'SoftLab-NSK Y16 + Alpha RLE',
    'FRWA': 'SoftLab-Nsk Forward Motion JPEG w/ alpha channel',
    'FRWD': 'SoftLab-Nsk Forward Motion JPEG',
    'FRWT': 'SoftLab-NSK Vision Forward Motion JPEG with Alpha-channel',
    'FRWU': 'SoftLab-NSK Vision Forward Uncompressed',
    'FVF1': 'Iterated Systems Fractal Video Frame',
    'FVFW': 'ff MPEG-4 based on XviD codec',
    'GEPJ': 'White Pine (ex Paradigm Matrix) Motion JPEG Codec',
    'GJPG': 'Grand Tech GT891x Codec',
    'GLCC': 'GigaLink AV Capture codec',
    'GLZW': 'Motion LZW',
    'GPEG': 'Motion JPEG',
    'GPJM': 'Pinnacle ReelTime MJPEG Codec',
    'GREY': 'Apparently a duplicate of Y800',
    'GWLT': 'Microsoft Greyscale WLT DIB',
    'H260': 'H.260',
    'H261': 'H.261',
    'H262': 'H.262',
    'H263': 'H.263',
    'H264': 'H.264 AVC',
    'H265': 'H.265 HEVC',
    'H266': 'H.266',
    'H267': 'H.267',
    'H268': 'H.268',
    'H269': 'H.269',
    'HD10': 'BlueFish444 (lossless RGBA, YUV 10-bit)',
    'HDX4': 'Jomigo HDX4',
    'HEVC': 'H.265 HEVC',
    'HFYU': 'Huffman Lossless Codec',
    'HMCR': 'Rendition Motion Compensation Format (HMCR)',
    'HMRR': 'Rendition Motion Compensation Format (HMRR)',
    'I263': 'Intel ITU H.263 Videoconferencing (i263)',
    'I420': 'Intel Indeo 4',
    'IAN ': 'Intel RDX',
    'ICLB': 'InSoft CellB Videoconferencing',
    'IDM0': 'IDM Motion Wavelets 2.0',
    'IF09': 'Microsoft H.261',
    'IGOR': 'Power DVD',
    'IJPG': 'Intergraph JPEG',
    'ILVC': 'Intel Layered Video',
    'ILVR': 'ITU-T H.263+',
    'IMC1': 'IMC1',
    'IMC2': 'IMC2',
    'IMC3': 'IMC3',
    'IMC4': 'IMC4',
    'IMJG': 'Accom SphereOUS MJPEG with Alpha-channel',
    'IPDV': 'I-O Data Device Giga AVI DV Codec',
    'IPJ2': 'Image Power JPEG2000',
    'IR21': 'Intel Indeo 2.1',
    'IRAW': 'Intel YUV Uncompressed',
    'IUYV': 'Interlaced version of UYVY (line order 0,2,4 then 1,3,5 etc)',
    'IV30': 'Ligos Indeo 3.0',
    'IV31': 'Ligos Indeo 3.1',
    'IV32': 'Ligos Indeo 3.2',
    'IV33': 'Ligos Indeo 3.3',
    'IV34': 'Ligos Indeo 3.4',
    'IV35': 'Ligos Indeo 3.5',
    'IV36': 'Ligos Indeo 3.6',
    'IV37': 'Ligos Indeo 3.7',
    'IV38': 'Ligos Indeo 3.8',
    'IV39': 'Ligos Indeo 3.9',
    'IV40': 'Ligos Indeo Interactive 4.0',
    'IV41': 'Ligos Indeo Interactive 4.1',
    'IV42': 'Ligos Indeo Interactive 4.2',
    'IV43': 'Ligos Indeo Interactive 4.3',
    'IV44': 'Ligos Indeo Interactive 4.4',
    'IV45': 'Ligos Indeo Interactive 4.5',
    'IV46': 'Ligos Indeo Interactive 4.6',
    'IV47': 'Ligos Indeo Interactive 4.7',
    'IV48': 'Ligos Indeo Interactive 4.8',
    'IV49': 'Ligos Indeo Interactive 4.9',
    'IV50': 'Ligos Indeo Interactive 5.0',
    'IY41': 'Interlaced version of Y41P (line order 0,2,4,...,1,3,5...)',
    'IYU1': '12 bit format used in mode 2 of the IEEE 1394 Digital Camera 1.04 spec',
    'IYU2': '24 bit format used in mode 2 of the IEEE 1394 Digital Camera 1.04 spec',
    'IYUV': 'Intel Indeo iYUV 4:2:0',
    'JBYR': 'Kensington JBYR',
    'JFIF': 'Motion JPEG (FFmpeg)',
    'JPEG': 'Still Image JPEG DIB',
    'JPG ': 'JPEG compressed',
    'JPGL': 'Webcam JPEG Light',
    'KMVC': 'Karl Morton\'s Video Codec',
    'KPCD': 'Kodak Photo CD',
    'L261': 'Lead Technologies H.261',
    'L263': 'Lead Technologies H.263',
    'LAGS': 'Lagarith LossLess',
    'LBYR': 'Creative WebCam codec',
    'LCMW': 'Lead Technologies Motion CMW Codec',
    'LCW2': 'LEADTools MCMW 9Motion Wavelet)',
    'LEAD': 'LEAD Video Codec',
    'LGRY': 'Lead Technologies Grayscale Image',
    'LJ2K': 'LEADTools JPEG2000',
    'LJPG': 'LEAD MJPEG Codec',
    'LMP2': 'LEADTools MPEG2',
    'LOCO': 'LOCO Lossless Codec',
    'LSCR': 'LEAD Screen Capture',
    'LSVM': 'Vianet Lighting Strike Vmail (Streaming)',
    'LZO1': 'LZO compressed (lossless codec)',
    'M261': 'Microsoft H.261',
    'M263': 'Microsoft H.263',
    'M4CC': 'ESS MPEG4 Divio codec',
    'M4S2': 'Microsoft MPEG-4 (M4S2)',
    'MC12': 'ATI Motion Compensation Format (MC12)',
    'MC24': 'MainConcept Motion JPEG Codec',
    'MCAM': 'ATI Motion Compensation Format (MCAM)',
    'MCZM': 'Theory MicroCosm Lossless 64bit RGB with Alpha-channel',
    'MDVD': 'Alex MicroDVD Video (hacked MS MPEG-4)',
    'MDVF': 'Pinnacle DV/DV50/DVHD100',
    'MHFY': 'A.M.Paredes mhuffyYUV (LossLess)',
    'MJ2C': 'Morgan Multimedia Motion JPEG2000',
    'MJPA': 'Pinnacle ReelTime MJPG hardware codec',
    'MJPB': 'Motion JPEG codec',
    'MJPG': 'Motion JPEG DIB',
    'MJPX': 'Pegasus PICVideo Motion JPEG',
    'MMES': 'Matrox MPEG-2 I-frame',
    'MNVD': 'MindBend MindVid LossLess',
    'MP2A': 'MPEG-2 Audio',
    'MP2T': 'MPEG-2 Transport Stream',
    'MP2V': 'MPEG-2 Video',
    'MP41': 'Microsoft MPEG-4 V1 (enhansed H263)',
    'MP42': 'Microsoft MPEG-4 (low-motion)',
    'MP43': 'Microsoft MPEG-4 (fast-motion)',
    'MP4A': 'MPEG-4 Audio',
    'MP4S': 'Microsoft MPEG-4 (MP4S)',
    'MP4T': 'MPEG-4 Transport Stream',
    'MP4V': 'Apple QuickTime MPEG-4 native',
    'MPEG': 'MPEG-1',
    'MPG1': 'FFmpeg-1',
    'MPG2': 'FFmpeg-1',
    'MPG3': 'Same as Low motion DivX MPEG-4',
    'MPG4': 'Microsoft MPEG-4 Video High Speed Compressor',
    'MPGI': 'Sigma Designs MPEG',
    'MPNG': 'Motion PNG codec',
    'MRCA': 'Martin Regen Codec',
    'MRLE': 'Run Length Encoding',
    'MSS1': 'Windows Screen Video',
    'MSS2': 'Windows Media 9',
    'MSUC': 'MSU LossLess',
    'MSVC': 'Microsoft Video 1',
    'MSZH': 'Lossless codec (ZIP compression)',
    'MTGA': 'Motion TGA images (24, 32 bpp)',
    'MTX1': 'Matrox MTX1',
    'MTX2': 'Matrox MTX2',
    'MTX3': 'Matrox MTX3',
    'MTX4': 'Matrox MTX4',
    'MTX5': 'Matrox MTX5',
    'MTX6': 'Matrox MTX6',
    'MTX7': 'Matrox MTX7',
    'MTX8': 'Matrox MTX8',
    'MTX9': 'Matrox MTX9',
    'MV12': 'MV12',
    'MVI1': 'Motion Pixels MVI',
    'MVI2': 'Motion Pixels MVI',
    'MWV1': 'Aware Motion Wavelets',
    'MYUV': 'Media-100 844/X Uncompressed',
    'NAVI': 'nAVI',
    'NDIG': 'Ahead Nero Digital MPEG-4 Codec',
    'NHVU': 'NVidia Texture Format (GEForce 3)',
    'NO16': 'Theory None16 64bit uncompressed RAW',
    'NT00': 'NewTek LigtWave HDTV YUV with Alpha-channel',
    'NTN1': 'Nogatech Video Compression 1',
    'NTN2': 'Nogatech Video Compression 2 (GrabBee hardware coder)',
    'NUV1': 'NuppelVideo',
    'NV12': '8-bit Y plane followed by an interleaved U/V plane with 2x2 subsampling',
    'NV21': 'As NV12 with U and V reversed in the interleaved plane',
    'NVDS': 'nVidia Texture Format',
    'NVHS': 'NVidia Texture Format (GEForce 3)',
    'NVS0': 'nVidia GeForce Texture',
    'NVS1': 'nVidia GeForce Texture',
    'NVS2': 'nVidia GeForce Texture',
    'NVS3': 'nVidia GeForce Texture',
    'NVS4': 'nVidia GeForce Texture',
    'NVS5': 'nVidia GeForce Texture',
    'NVT0': 'nVidia GeForce Texture',
    'NVT1': 'nVidia GeForce Texture',
    'NVT2': 'nVidia GeForce Texture',
    'NVT3': 'nVidia GeForce Texture',
    'NVT4': 'nVidia GeForce Texture',
    'NVT5': 'nVidia GeForce Texture',
    'PDVC': 'I-O Data Device Digital Video Capture DV codec',
    'PGVV': 'Radius Video Vision',
    'PHMO': 'IBM Photomotion',
    'PIM1': 'Pegasus Imaging',
    'PIM2': 'Pegasus Imaging',
    'PIMJ': 'Pegasus Imaging Lossless JPEG',
    'PIXL': 'MiroVideo XL (Motion JPEG)',
    'PNG ': 'Apple PNG',
    'PNG1': 'Corecodec.org CorePNG Codec',
    'PVEZ': 'Horizons Technology PowerEZ',
    'PVMM': 'PacketVideo Corporation MPEG-4',
    'PVW2': 'Pegasus Imaging Wavelet Compression',
    'PVWV': 'Pegasus Imaging Wavelet 2000',
    'PXLT': 'Apple Pixlet (Wavelet)',
    'Q1.0': 'Q-Team QPEG 1.0 (www.q-team.de)',
    'Q1.1': 'Q-Team QPEG 1.1 (www.q-team.de)',
    'QDGX': 'Apple QuickDraw GX',
    'QPEG': 'Q-Team QPEG 1.0',
    'QPEQ': 'Q-Team QPEG 1.1',
    'R210': 'BlackMagic YUV (Quick Time)',
    'R411': 'Radius DV NTSC YUV',
    'R420': 'Radius DV PAL YUV',
    'RAVI': 'GroupTRON ReferenceAVI codec (dummy for MPEG compressor)',
    'RAV_': 'GroupTRON ReferenceAVI codec (dummy for MPEG compressor)',
    'RAW ': 'Full Frames (Uncompressed)',
    'RGB ': 'Full Frames (Uncompressed)',
    'RGB(15)': 'Uncompressed RGB15 5:5:5',
    'RGB(16)': 'Uncompressed RGB16 5:6:5',
    'RGB(24)': 'Uncompressed RGB24 8:8:8',
    'RGB1': 'Uncompressed RGB332 3:3:2',
    'RGBA': 'Raw RGB with alpha',
    'RGBO': 'Uncompressed RGB555 5:5:5',
    'RGBP': 'Uncompressed RGB565 5:6:5',
    'RGBQ': 'Uncompressed RGB555X 5:5:5 BE',
    'RGBR': 'Uncompressed RGB565X 5:6:5 BE',
    'RGBT': 'Computer Concepts 32-bit support',
    'RL4 ': 'RLE 4bpp RGB',
    'RL8 ': 'RLE 8bpp RGB',
    'RLE ': 'Microsoft Run Length Encoder',
    'RLE4': 'Run Length Encoded 4',
    'RLE8': 'Run Length Encoded 8',
    'RMP4': 'REALmagic MPEG-4 Video Codec',
    'ROQV': 'Id RoQ File Video Decoder',
    'RPZA': 'Apple Video 16 bit "road pizza"',
    'RT21': 'Intel Real Time Video 2.1',
    'RTV0': 'NewTek VideoToaster',
    'RUD0': 'Rududu video codec',
    'RV10': 'RealVideo codec',
    'RV13': 'RealVideo codec',
    'RV20': 'RealVideo G2',
    'RV30': 'RealVideo 8',
    'RV40': 'RealVideo 9',
    'RVX ': 'Intel RDX (RVX )',
    'S263': 'Sorenson Vision H.263',
    'S422': 'Tekram VideoCap C210 YUV 4:2:2',
    'SAMR': 'Adaptive Multi-Rate (AMR) audio codec',
    'SAN3': 'MPEG-4 codec (direct copy of DivX 3.11a)',
    'SDCC': 'Sun Communication Digital Camera Codec',
    'SEDG': 'Samsung MPEG-4 codec',
    'SFMC': 'CrystalNet Surface Fitting Method',
    'SHR0': 'BitJazz SheerVideo',
    'SHR1': 'BitJazz SheerVideo',
    'SHR2': 'BitJazz SheerVideo',
    'SHR3': 'BitJazz SheerVideo',
    'SHR4': 'BitJazz SheerVideo',
    'SHR5': 'BitJazz SheerVideo',
    'SHR6': 'BitJazz SheerVideo',
    'SHR7': 'BitJazz SheerVideo',
    'SJPG': 'CUseeMe Networks Codec',
    'SL25': 'SoftLab-NSK DVCPRO',
    'SL50': 'SoftLab-NSK DVCPRO50',
    'SLDV': 'SoftLab-NSK Forward DV Draw codec',
    'SLIF': 'SoftLab-NSK MPEG2 I-frames',
    'SLMJ': 'SoftLab-NSK Forward MJPEG',
    'SMC ': 'Apple Graphics (SMC) codec (256 color)',
    'SMSC': 'Radius SMSC',
    'SMSD': 'Radius SMSD',
    'SMSV': 'WorldConnect Wavelet Video',
    'SNOW': 'SNOW codec',
    'SP40': 'SunPlus YUV',
    'SP44': 'SunPlus Aiptek MegaCam Codec',
    'SP53': 'SunPlus Aiptek MegaCam Codec',
    'SP54': 'SunPlus Aiptek MegaCam Codec',
    'SP55': 'SunPlus Aiptek MegaCam Codec',
    'SP56': 'SunPlus Aiptek MegaCam Codec',
    'SP57': 'SunPlus Aiptek MegaCam Codec',
    'SP58': 'SunPlus Aiptek MegaCam Codec',
    'SPIG': 'Radius Spigot',
    'SPLC': 'Splash Studios ACM Audio Codec',
    'SPRK': 'Sorenson Spark',
    'SQZ2': 'Microsoft VXTreme Video Codec V2',
    'STVA': 'ST CMOS Imager Data (Bayer)',
    'STVB': 'ST CMOS Imager Data (Nudged Bayer)',
    'STVC': 'ST CMOS Imager Data (Bunched)',
    'STVX': 'ST CMOS Imager Data (Extended CODEC Data Format)',
    'STVY': 'ST CMOS Imager Data (Extended CODEC Data Format with Correction Data)',
    'SV10': 'Sorenson Video R1',
    'SVQ1': 'Sorenson Video R3',
    'SVQ3': 'Sorenson Video 3 (Apple Quicktime 5)',
    'SWC1': 'MainConcept Motion JPEG Codec',
    'T420': 'Toshiba YUV 4:2:0',
    'TGA ': 'Apple TGA (with Alpha-channel)',
    'THEO': 'FFVFW Supported Codec',
    'TIFF': 'Apple TIFF (with Alpha-channel)',
    'TIM2': 'Pinnacle RAL DVI',
    'TLMS': 'TeraLogic Motion Intraframe Codec (TLMS)',
    'TLST': 'TeraLogic Motion Intraframe Codec (TLST)',
    'TM20': 'Duck TrueMotion 2.0',
    'TM2A': 'Duck TrueMotion Archiver 2.0',
    'TM2X': 'Duck TrueMotion 2X',
    'TMIC': 'TeraLogic Motion Intraframe Codec (TMIC)',
    'TMOT': 'Horizons Technology TrueMotion S',
    'TR20': 'Duck TrueMotion RealTime 2.0',
    'TRLE': 'Akula Alpha Pro Custom AVI (LossLess)',
    'TSCC': 'TechSmith Screen Capture Codec',
    'TV10': 'Tecomac Low-Bit Rate Codec',
    'TVJP': 'TrueVision Field Encoded Motion JPEG',
    'TVMJ': 'Truevision TARGA MJPEG Hardware Codec',
    'TY0N': 'Trident TY0N',
    'TY2C': 'Trident TY2C',
    'TY2N': 'Trident TY2N',
    'U263': 'UB Video StreamForce H.263',
    'U<Y ': 'Discreet UC YUV 4:2:2:4 10 bit',
    'U<YA': 'Discreet UC YUV 4:2:2:4 10 bit (with Alpha-channel)',
    'UCOD': 'eMajix.com ClearVideo',
    'ULTI': 'IBM Ultimotion',
    'UMP4': 'UB Video MPEG 4',
    'UYNV': 'UYVY',
    'UYVP': 'YCbCr 4:2:2',
    'UYVU': 'SoftLab-NSK Forward YUV codec',
    'UYVY': 'UYVY 4:2:2 byte ordering',
    'V210': 'Optibase VideoPump 10-bit 4:2:2 Component YCbCr',
    'V261': 'Lucent VX2000S',
    'V422': '24 bit YUV 4:2:2 Format',
    'V655': '16 bit YUV 4:2:2 Format',
    'VBLE': 'MarcFD VBLE Lossless Codec',
    'VCR1': 'ATI VCR 1.0',
    'VCR2': 'ATI VCR 2.0',
    'VCR3': 'ATI VCR 3.0',
    'VCR4': 'ATI VCR 4.0',
    'VCR5': 'ATI VCR 5.0',
    'VCR6': 'ATI VCR 6.0',
    'VCR7': 'ATI VCR 7.0',
    'VCR8': 'ATI VCR 8.0',
    'VCR9': 'ATI VCR 9.0',
    'VDCT': 'Video Maker Pro DIB',
    'VDOM': 'VDOnet VDOWave',
    'VDOW': 'VDOnet VDOLive (H.263)',
    'VDST': 'VirtualDub remote frameclient ICM driver',
    'VDTZ': 'Darim Vison VideoTizer YUV',
    'VGPX': 'VGPixel Codec',
    'VIDM': 'DivX 5.0 Pro Supported Codec',
    'VIDS': 'YUV 4:2:2 CCIR 601 for V422',
    'VIFP': 'VIFP',
    'VIV1': 'Vivo H.263',
    'VIV2': 'Vivo H.263',
    'VIVO': 'Vivo H.263 v2.00',
    'VIXL': 'Miro Video XL',
    'VLV1': 'Videologic VLCAP.DRV',
    'VP30': 'On2 VP3.0',
    'VP31': 'On2 VP3.1',
    'VP40': 'On2 TrueCast VP4',
    'VP50': 'On2 TrueCast VP5',
    'VP60': 'On2 TrueCast VP6',
    'VP61': 'On2 TrueCast VP6.1',
    'VP62': 'On2 TrueCast VP6.2',
    'VP70': 'On2 TrueMotion VP7',
    'VQC1': 'Vector-quantised codec 1',
    'VQC2': 'Vector-quantised codec 2',
    'VR21': 'BlackMagic YUV (Quick Time)',
    'VSSH': 'Vanguard VSS H.264',
    'VSSV': 'Vanguard Software Solutions Video Codec',
    'VSSW': 'Vanguard VSS H.264',
    'VTLP': 'Alaris VideoGramPixel Codec',
    'VX1K': 'VX1000S Video Codec',
    'VX2K': 'VX2000S Video Codec',
    'VXSP': 'VX1000SP Video Codec',
    'VYU9': 'ATI Technologies YUV',
    'VYUY': 'ATI Packed YUV Data',
    'WBVC': 'Winbond W9960',
    'WHAM': 'Microsoft Video 1 (WHAM)',
    'WINX': 'Winnov Software Compression',
    'WJPG': 'AverMedia Winbond JPEG',
    'WMV1': 'Windows Media Video V7',
    'WMV2': 'Windows Media Video V8',
    'WMV3': 'Windows Media Video V9',
    'WMVA': 'WMVA codec',
    'WMVP': 'Windows Media Video V9',
    'WNIX': 'WniWni Codec',
    'WNV1': 'Winnov Hardware Compression',
    'WNVA': 'Winnov hw compress',
    'WRLE': 'Apple QuickTime BMP Codec',
    'WRPR': 'VideoTools VideoServer Client Codec',
    'WV1F': 'WV1F codec',
    'WVLT': 'IllusionHope Wavelet 9/7',
    'WVP2': 'WVP2 codec',
    'X263': 'Xirlink H.263',
    'X264': 'XiWave GNU GPL x264 MPEG-4 Codec',
    'X265': 'H.265 HEVC',
    'XLV0': 'NetXL Video Decoder',
    'XMPG': 'Xing MPEG (I-Frame only)',
    'XVID': 'XviD MPEG-4',
    'XVIX': 'Based on XviD MPEG-4 codec',
    'XWV0': 'XiWave Video Codec',
    'XWV1': 'XiWave Video Codec',
    'XWV2': 'XiWave Video Codec',
    'XWV3': 'XiWave Video Codec (Xi-3 Video)',
    'XWV4': 'XiWave Video Codec',
    'XWV5': 'XiWave Video Codec',
    'XWV6': 'XiWave Video Codec',
    'XWV7': 'XiWave Video Codec',
    'XWV8': 'XiWave Video Codec',
    'XWV9': 'XiWave Video Codec',
    'XXAN': 'XXAN',
    'XYZP': 'Extended PAL format XYZ palette',
    'Y211': 'YUV 2:1:1 Packed',
    'Y216': 'Pinnacle TARGA CineWave YUV (Quick Time)',
    'Y411': 'YUV 4:1:1 Packed',
    'Y41B': 'YUV 4:1:1 Planar',
    'Y41P': 'PC1 4:1:1',
    'Y41T': 'PC1 4:1:1 with transparency',
    'Y422': 'Y422',
    'Y42B': 'YUV 4:2:2 Planar',
    'Y42T': 'PCI 4:2:2 with transparency',
    'Y444': 'IYU2',
    'Y8  ': 'Grayscale video',
    'Y800': 'Simple grayscale video',
    'YC12': 'Intel YUV12 Codec',
    'YMPG': 'YMPEG Alpha',
    'YU12': 'ATI YV12 4:2:0 Planar',
    'YU92': 'Intel - YUV',
    'YUNV': 'YUNV',
    'YUV2': 'Apple Component Video (YUV 4:2:2)',
    'YUV8': 'Winnov Caviar YUV8',
    'YUV9': 'Intel YUV9',
    'YUVP': 'YCbCr 4:2:2',
    'YUY2': 'Uncompressed YUV 4:2:2',
    'YUYV': 'Canopus YUV',
    'YV12': 'YVU12 Planar',
    'YV16': 'Elecard YUV 4:2:2 Planar',
    'YV92': 'Intel Smart Video Recorder YVU9',
    'YVU9': 'Intel YVU9 Planar',
    'YVYU': 'YVYU 4:2:2 byte ordering',
    'ZLIB': 'ZLIB',
    'ZPEG': 'Metheus Video Zipper',
    'ZYGO': 'ZyGo Video Codec'
}

# make it fool prove
for code, value in list(FOURCC.items()):
    if not code.upper() in FOURCC:
        FOURCC[code.upper()] = value
    if code.endswith(' '):
        FOURCC[code.strip().upper()] = value
