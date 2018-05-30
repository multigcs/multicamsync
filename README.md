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
* initial offsets are read from file-timestamps
* You can set the offset of a complete track and of each single file
* there are some corrections for different camera types in cameras.json
```json
	{
		"EOS M": "CSTAMP",
		"Canon EOS M": "CSTAMP",
		"M6": "CSTAMP",
		"Canon EOS M6": "CSTAMP",
		"EOS M3": "CSTAMP_MINUS_LEN",
		"Canon EOS M3": "CSTAMP_MINUS_LEN",
		"EOS 6D": "CSTAMP",
		"Canon EOS 6D": "CSTAMP",
		"Canon EOS 5D Mark II": "CSTAMP",
		"HG310": "CSTAMP",
		"Panasonic": "CSTAMP",
		"SESSION": "FSTAMP"
	}
```

## Export
* XMEML-Project (tested with Lightworks)
* Kdenlive-Project (tested with Kdenlive)

## Depends
* python3-opencv
* python3-gi
* python3-gi-cairo
* ffmpeg (for Thumbnail-Images)
* exiftool (for Exif-Infos)


