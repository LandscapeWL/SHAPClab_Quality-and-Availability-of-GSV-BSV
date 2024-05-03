# SHAPClab_Quality-and-Availability-of-GSV-BSV
In this study, we collected panoramic street views within the Fifth Ring Road of Beijing using the Baidu Maps platform. We transformed these panoramic images into fisheye views and calculated the sun's trajectory during the summer. Based on this data, we estimated the solar radiation in the city. Furthermore, we innovatively used the street view collection parameters to determine the orientation of the street network. We analyzed the influence of the street network's orientation on solar radiation in both temporal and spatial dimensions. All our foundational data is available in this GitHub project, which can be used for extension, verification, replication, and enhancement of our research.

# Information
The research is carried out under the SHAPC-lab and the lab director & the corresponding author:Jie He academic social networks page:<br>
http://faculty.hitsz.edu.cn/hejie

For more information related to the research, please follow the laboratory's WeChat Official Account:<br>
![空间人文与场所计算](http://photogz.photo.store.qq.com/psc?/V51wK6B50SnpHF0Ql90V120XkX2YMvAu/bqQfVz5yrrGYSXMvKr.cqaGvn*U8.XtKGUKoCXp2T7*rr64Fh949noTXvtqynumAfdG91L2EpB0ozp5TDQDefp4ivWRqPAlBcUTccYj7QHE!/b&bo=lgGcAZYBnAEBByA!&rf=viewer_4 "空间人文与场所计算")
# Project Introduction
This project focuses on a comprehensive comparative analysis of Street View Images (SVI) from two major mapping service platforms: Google Street View (GSV) and Baidu Street View (BSV). As an important geospatial data type, street view images are widely used in various urban environment analyses. Through this research, we systematically evaluated the data differences, image quality, and availability of GSV and BSV in cities globally for the first time.

# Key Features

- Data Difference Comparison: Detailed comparison of over 700,000 street view images from GSV and BSV in the same cities to identify data discrepancies.

- Quality Assessment: Assessed the quality differences of street view images in terms of field of view, pixel density, interval, and aspect ratio.

- Parameter Standardization: Defined a set of unified parameter standards for using GSV and BSV data to facilitate interoperability between the two datasets.

- Urban Evaluation Effectiveness: Explored the effectiveness of street view images in describing urban environmental features under varying distances and time parameters.

- Error Analysis: Demonstrated that the errors in representing urban environmental elements by both platforms are within acceptable limits, with consistent usability of results.

# Requirements
- Pandas
- Numpy
- Matplotlib
- sklearn
- shapely
- geopandas
- sqlite3
# Usage
- 202310Metadata_StreetView
<br>`Collect street view metadata`<br>
- 202401caculate_repeat
<br>`Calculate the effectiveness of street view acquisition with different spacing`<br>
- 202404caculate_segmentation
<br>`Calculate the correlation between GSV and BSV visual elements`<br>

