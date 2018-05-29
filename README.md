# multicamsync
Multi-Camera Syncing-Tool


![Screenshot](https://raw.githubusercontent.com/multigcs/multicamsync/master/screenshot.png)


## Warning
* **alpha-version !!!**
* **only testet on Linux !!!**
* **only with one Project !!!**
* **no audio-support !!!**

## Import
* Designed to import an Folder Structure like this:
	* ./5d-card1/DCIM/100EOS5D/MVI_0565.MOV
	* ./5d-card1/DCIM/100EOS5D/MVI_0563.MOV
	* ./5d-card1/DCIM/100EOS5D/MVI_0571.MOV
	* ./5d-card2/DCIM/100EOS5D/MVI_0183.MOV
	* ./5d-card2/DCIM/100EOS5D/MVI_0180.MOV
	* ./5d-card2/DCIM/100EOS5D/MVI_0191.MOV
	* ./5d-card3/DCIM/100EOS5D/MVI_3431.MOV
	* ./5d-card3/DCIM/100EOS5D/MVI_3429.MOV
	* ./5d-card3/DCIM/100EOS5D/MVI_3438.MOV
	* ./OSMO/DCIM/100MEDIA/DJI_0002.MOV
	* ./OSMO/DCIM/100MEDIA/DJI_0001.MOV
	* ./OSMO/DCIM/100MEDIA/DJI_0003.MOV
	* ./M6/DCIM/100CANON/MVI_9688.MOV
	* ./M6/DCIM/100CANON/MVI_9684.MOV
	* ./M6/DCIM/100CANON/MVI_9691.MOV
	* ./M6/DCIM/100CANON/MVI_9685.MOV
	* ./6D/100CANON/MVI_2276.MOV
	* ./6D/100CANON/MVI_2314.MOV
	* ./6D/100CANON/MVI_2312.MOV
	* ./6D/100CANON/MVI_2287.MOV

## Edit
* each main folder becomes a track
* initial offsets are read from file-timestamps, there are some corrections for different camera types
	* ["Canon EOS M"] = self.CSTAMP # using create date from meta-info
	* ["Canon EOS M3"] = self.CSTAMP_MINUS_LEN # using create date from meta-info minus media-length
	* ["SESSION"] = self.FSTAMP # using filestamp (last modify)
	* .....
* You can set the offset of a complete track and of each single file

## Export
* XMEML and Kdenlive Export


