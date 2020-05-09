import fcntl
import time
import unittest
from ctypes import *
import math
import struct
import binascii

class TSD305 :
	# TSD305 device address
	_TSD305_ADDR = 0x1e #0b0110000
	
	# TSD305 device commands
	_TSD305_CONVERT_ADCS_COMMAND = 0xaf
	_TSD305_STATUS_BUSY_MASK = 0x20
	_TSD305_STATUS_MEMOTY_ERROR_MASK = 0x04
	_TSD305_CONVERSION_TIME = 0.1
	
	_TSD305_LOT_NUMBER = 0x00
	_TSD305_SERIAL_NUMBER = 0x01
	
	# TSD305 commands read eeprom
	_TSD305_MIN_AMBIENT_TEMPERATURE = 0x1A
	_TSD305_MAX_AMBIENT_TEMPERATURE = 0x1B
	_TSD305_MIN_OBJECT_TEMPERATURE = 0x1C
	_TSD305_MAX_OBJECT_TEMPERATURE = 0x1D
	_TSD305_TEMPERATURE_COEFF1 = 0x1E
	_TSD305_TEMPERATURE_COEFF2 = 0x1F
	_TSD305_TEMPERATURE_REF1 = 0x20
	_TSD305_TEMPERATURE_REF2 = 0x21
	_TSD305_COFF_COMPENSATION_K41 = 0x22
	_TSD305_COFF_COMPENSATION_K31 = 0x24
	_TSD305_COFF_COMPENSATION_K21 = 0x26
	_TSD305_COFF_COMPENSATION_K11 = 0x28
	_TSD305_COFF_COMPENSATION_K01 = 0x2A
	_TSD305_COFF_COMPENSATION_K42 = 0x23
	_TSD305_COFF_COMPENSATION_K32 = 0x25
	_TSD305_COFF_COMPENSATION_K22 = 0x27
	_TSD305_COFF_COMPENSATION_K12 = 0x29
	_TSD305_COFF_COMPENSATION_K02 = 0x2B
	_TSD305_ADC_T_COFF_K41 = 0x2E
	_TSD305_ADC_T_COFF_K31 = 0x30
	_TSD305_ADC_T_COFF_K21 = 0x32
	_TSD305_ADC_T_COFF_K11 = 0x34
	_TSD305_ADC_T_COFF_K01 = 0x36
	_TSD305_ADC_T_COFF_K42 = 0x2F
	_TSD305_ADC_T_COFF_K32 = 0x31
	_TSD305_ADC_T_COFF_K22 = 0x33
	_TSD305_ADC_T_COFF_K12 = 0x35
	_TSD305_ADC_T_COFF_K02 = 0x37

	_TSD305_LUT_AMBIENT_SIZE = 22
	_TSD305_LUT_ADC_SIZE = 21
	
	coeff_valid = False

	object_temperature_lut = [
		[ 0, 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100],
		[ -20, 935975, 1202135, 1482033, 1776117, 2084843, 2408670, 2748065, 3103501, 3475458, 3864419, 4270880, 4695336, 5138293, 5600262, 6081756, 6583301, 7105426, 7648664, 8213558, 8800655, 9410506 ],
		[ -15, 706695, 967783, 1242348, 1530828, 1833670, 2151327, 2484255, 2832918, 3197786, 3579336, 3978052, 4394420, 4828936, 5282101, 5754421, 6246409, 6758583, 7291471, 7845600, 8421509, 9019740 ],
		[ -10, 474076, 730091, 999323, 1282199, 1579159, 1890644, 2217105, 2558995, 2916776, 3290914, 3681884, 4090164, 4516239, 4960601, 5423746, 5906177, 6408402, 6930938, 7474302, 8039024, 8625634 ],
		[ -5, 238406, 489349, 753247, 1030519, 1321597, 1626911, 1946904, 2282021, 2632714, 2999441, 3382665, 3782858, 4200492, 4636050, 5090020, 5562893, 6055169, 6567354, 7099955, 7653488, 8228477 ],
		[ 0, 0, 245872, 504435, 776105, 1061298, 1360443, 1673967, 2002311, 2345917, 2705232, 3080712, 3472815, 3882009, 4308764, 4753558, 5216875, 5699202, 6201033, 6722870, 7265216, 7828584 ],
		[ 5, -240800, 0, 25323, 519295, 798606, 1091580, 1398638, 1720208, 2056726, 2408629, 2776363, 3160378, 3561131, 3979083, 4414703, 4868463, 5340840, 5832320, 6343392, 6874552, 7426298 ],
		[ 10, -483624, -247897, 0, 260461, 533890, 820692, 1121283, 1436081, 1765510, 2110002, 2469990, 2845917, 3238230, 3647379, 4073823, 4518025, 4980453, 5461582, 5961890, 6481861, 7021987 ],
		[ 15, -728077, -497420, -254857, 0, 267545, 548177, 842301, 1150326, 1472668, 1809746, 2161990, 2529828, 2913700, 3314047, 3731315, 4165961, 4618439, 5089216, 5578759, 6087544, 6616048 ],
		[ 20, -973729, -748144, -510916, -261662, 0, 274462, 562117, 863369, 1178623, 1508291, 1852789, 2212539, 2587970, 2979513, 3387607, 3812695, 4255225, 4715649, 5194429, 5692026, 6208909 ],
		[ 25, -1220128, -999615, -767719, -524070, -268291, 0, 281189, 575668, 883834, 1206089, 1542842, 1894504, 2261494, 2644235, 3043154, 3458684, 3891264, 4341338, 4809352, 5295762, 5801025 ],
		[ 30, -1466786, -1251346, -1024783, -786738, -536841, -274722, 0, 287706, 588784, 903628, 1232635, 1576210, 1934759, 2308696, 2698440, 3104413, 3527043, 3966766, 4424016, 4899238, 5392880 ],
		[ 35, -1713188, -1502819, -1281591, -1049150, -805136, -549187, -280933, 0, 293990, 601423, 922684, 1258170, 1608279, 1973413, 2353982, 2750397, 3163080, 3592449, 4038935, 4502970, 4984991 ],
		[ 40, -1958788, -1753491, -1537596, -1310759, -1072627, -822849, -561062, -286903, 0, 300020, 613536, 940935, 1282602, 1638933, 2010327, 2397185, 2799918, 3218936, 3654658, 4107505, 4577905 ],
		[ 45, -2203005, -2002779, -1792219, -1570984, -1338737, -1095129, -839810, -572423, -292608, 0, 305772, 625081, 958308, 1305836, 1668054, 2045356, 2438139, 2846805, 3271763, 3713423, 4172201 ],
		[ 50, -2445228, -2250074, -2044846, -1829217, -1602853, -1365415, -1116563, -855949, -583222, -298026, 0, 311221, 636007, 974733, 1327775, 1695520, 2078353, 2476669, 2890861, 3321334, 3768491 ],
		[ 55, -2684813, -2494731, -2294837, -2084811, -1864329, -1633062, -1390678, -1136837, -871198, -593414, -303133, 0, 316345, 646267, 990135, 1348323, 1721207, 2109170, 2512599, 2931884, 3367420 ],
		[ 60, -2921081, -2736070, -2541511, -2337088, -2122490, -1897393, -1661477, -1414409, -1155858, -885485, -602949, -307905, 0, 321119, 655812, 1004442, 1367377, 1744988, 2137653, 2545751, 2969666 ],
		[ 65, -3153319, -2973381, -2784154, -2585337, -2376620, -2157696, -1928246, -1687951, -1436487, -1173526, -898737, -611780, -312316, 0, 325518, 664590, 1017576, 1384836, 1766736, 2163646, 2575941 ],
		[ 70, -3380782, -3205915, -3022022, -2828808, -2625975, -2413221, -2190238, -1956716, -1712341, -1456792, -1189747, -910879, -619856, -316343, 0, 329515, 672552, 1029460, 1400596, 1786318, 2186992 ],
		[ 75, -3602685, -3432890, -3254330, -3066721, -2869771, -2663187, -2446671, -2219922, -1982635, -1734498, -1475198, -1204419, -921836, -627126, -319958, 0, 333087, 679644, 1040014, 1414550, 1803603 ],
		[ 80, -3818210, -3653487, -3480260, -3298254, -3107188, -2906774, -2696726, -2476751, -2246551, -2005826, -1754271, -1491580, -1217438, -931531, -633539, -323137, 0, 336205, 685812, 1049160, 1426591 ],
		[ 85, -4026501, -3866849, -3698957, -3522555, -3337371, -3143129, -2939548, -2726345, -2503233, -2269920, -2026111, -1771507, -1505806, -1228703, -939885, -639041, -325853, 0, 338843, 691003, 1056813 ]
	];
	
	# Init result eeprom coeff
	class eeprom_coeff : 
		lot_number = 0x0000
		serial_number = 0x0000
		min_ambient_temperature = 0
		max_ambient_temperature = 0
		min_object_temperature = 0x0000
		max_object_temperature = 0x0000
	
	#From: /linux/i2c-dev.h
	I2C_SLAVE = 0x0703
	I2C_SLAVE_FORCE = 0x0706

	def __init__(self, device_number=0) :
		self.i2c = open('/dev/i2c-%s'%(device_number),'r+',0)
		fcntl.ioctl(self.i2c, self.I2C_SLAVE, self._TSD305_ADDR)
		time.sleep(0.015)

	# brief read eeprom coeff.
	# \param[in] address of coefficient in EEPROM
	# return :
	#		-> Data read 
	def readeeprom_coeff (self, address) : 
		self.i2c.write(chr(address))
		time.sleep(0.001)
		data = self.i2c.read(3)
		val = (ord(data[1]) * 0x100) + ord(data[2])
		if val > 0x7fff:
			val -= 0x10000
		time.sleep(0.01)
		return val

	def read_data(self, address):
		self.i2c.write(chr(address))
		time.sleep(0.001)
		data = self.i2c.read(4)
		return hex((ord(data[1]) * 0x100) + ord(data[2]))

	#\brief Reads the TSD305 EEPROM coefficients to store them for computation.
	# return :
	#		-> All coefficients read in the EEPROM 
	def read_eeprom (self) :
		
		self.eeprom_coeff.lot_number = self.readeeprom_coeff(self._TSD305_LOT_NUMBER)
		self.eeprom_coeff.serial_number = self.readeeprom_coeff(self._TSD305_SERIAL_NUMBER)
		self.eeprom_coeff.min_ambient_temperature = self.readeeprom_coeff(self._TSD305_MIN_AMBIENT_TEMPERATURE)
		self.eeprom_coeff.max_ambient_temperature = self.readeeprom_coeff(self._TSD305_MAX_AMBIENT_TEMPERATURE)
			
		self.eeprom_coeff.min_object_temperature = self.readeeprom_coeff(self._TSD305_MIN_OBJECT_TEMPERATURE)
		self.eeprom_coeff.max_object_temperature = self.readeeprom_coeff(self._TSD305_MAX_OBJECT_TEMPERATURE)
				
		return True

	# brief Triggers conversion and read ADC value
	# \param[in] : None
	# return :
	#		-> Adc value
	def conversion_and_read_adcs (self) :
		self.i2c.write(chr(self._TSD305_CONVERT_ADCS_COMMAND))
		time.sleep(self._TSD305_CONVERSION_TIME)
		data = self.i2c.read(7)
				
		adc_object = (ord(data[1]) * 0x10000) + (ord(data[2]) * 0x100) + ord(data[3])
		adc_ambient = (ord(data[4]) * 0x10000) + (ord(data[5]) * 0x100) + ord(data[6])
		return adc_object,adc_ambient

	def ieeeToDecimal(self, addr1, addr2):
		h = int(self.read_data(addr1),16) << 16
		l = int(self.read_data(addr2),16)
		fullhex = h + l
		hexstring = hex(fullhex)[2:10]
		ret = struct.unpack('>f',binascii.unhexlify(hexstring))[0]
		return ret






	# brief Reads the temperature and pressure ADC value and compute the compensated values.
	# \param[in] : None
	# return :
	#		-> Ambient temperature (float) : Celsius Degree temperature value
	#		-> Object temperature (float) : mbar pressure value
	def read_temperature_and_object_temperature (self) : 
		if self.coeff_valid == False :
			self.coeff_valid = self.read_eeprom()
		(adc_object, adc_ambient) = self.conversion_and_read_adcs()

		temperature = float(adc_ambient) / 16777216.0 * float(self.eeprom_coeff.max_ambient_temperature - self.eeprom_coeff.min_ambient_temperature) + float(self.eeprom_coeff.min_ambient_temperature)
		#Page 9 of Datasheet
		tref = self.ieeeToDecimal(self._TSD305_TEMPERATURE_REF1, self._TSD305_TEMPERATURE_REF2)
		tc = self.ieeeToDecimal(self._TSD305_TEMPERATURE_COEFF1, self._TSD305_TEMPERATURE_COEFF2)
		tcf = 1 + ((temperature - tref) * tc)
		
		#Page 10 of Datasheet
		compK4 = self.ieeeToDecimal(self._TSD305_COFF_COMPENSATION_K41,self._TSD305_COFF_COMPENSATION_K42)
		compK3 = self.ieeeToDecimal(self._TSD305_COFF_COMPENSATION_K31,self._TSD305_COFF_COMPENSATION_K32)
		compK2 = self.ieeeToDecimal(self._TSD305_COFF_COMPENSATION_K21,self._TSD305_COFF_COMPENSATION_K22)
		compK1 = self.ieeeToDecimal(self._TSD305_COFF_COMPENSATION_K11,self._TSD305_COFF_COMPENSATION_K12)
		compK0 = self.ieeeToDecimal(self._TSD305_COFF_COMPENSATION_K01,self._TSD305_COFF_COMPENSATION_K02)
		offset = (compK4 * (temperature**4)) + (compK3 * (temperature**3)) + (compK2 * (temperature**2)) + (compK1 * (temperature)) + (compK0)
		offset_tc = offset * tcf

		#Page 11 of Datasheet
		adc_comp = offset_tc + adc_object - 8388608
		adc_comp_tc = adc_comp / tcf
		adctK4 = self.ieeeToDecimal(self._TSD305_ADC_T_COFF_K41,self._TSD305_ADC_T_COFF_K42)
		adctK3 = self.ieeeToDecimal(self._TSD305_ADC_T_COFF_K31,self._TSD305_ADC_T_COFF_K32)
		adctK2 = self.ieeeToDecimal(self._TSD305_ADC_T_COFF_K21,self._TSD305_ADC_T_COFF_K22)
		adctK1 = self.ieeeToDecimal(self._TSD305_ADC_T_COFF_K11,self._TSD305_ADC_T_COFF_K12)
		adctK0 = self.ieeeToDecimal(self._TSD305_ADC_T_COFF_K01,self._TSD305_ADC_T_COFF_K02)
		object_temperature = (adctK4 * (adc_comp_tc**4)) + (adctK3 * (adc_comp_tc**3)) + (adctK2 * (adc_comp_tc**2)) + (adctK1 * (adc_comp_tc)) + (adctK0)

		return temperature, object_temperature

	def close(self):
		self.i2c.close()

	def __enter__(self):
		return self		

	def __exit__(self, type, value, traceback):
		self.close()
