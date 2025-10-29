Snapdeal Product Data Analysis

1. Objective of the Project-
The main objective of this project is to analyze product pricing, discounting patterns, and customer satisfaction levels to identify business insights and optimization opportunities for an e-commerce  platform (Snapdeal). The goal is to uncover how price and discount impact ratings and overall customer perception.

2. Dataset Overview-
Column Name	    Description
Product Name	  Name of the product sold
Original Price	Original listed price before discount
Price	Final     selling price after discount
Discount	      Percentage discount offered
Rating	        Average customer rating (out of 5)
Price Bin	      Grouped price ranges for analysis
Discount Bin  	Grouped discount percentage ranges
Subcategory	    Product classification
Scraping Date  	Date when product data was collected

4. Data Cleaning & Preparation-
- Removed duplicate entries and missing values
- Verified numeric columns (Price, Discount, Rating)
- Created calculated columns such as Discount % and Price/Discount Bins
-Created columns link color, binding ,pack of, waterproof etc.
- Ensured correct data types for Date and Numeric fields

4. Visualizations -
A. Discount vs count (column chart)
The chart shows the count of total products for each discount Bin.
B. Subcategory by product count(Pie chart)
This visualization shows count of products for each subcategory and their percentage.
C. Price  vs Rating(Line chart)
The line chart shows rating and review count as per price.
D. Average Rating by subcategory (Tree map)
This visualization shows  average rating  for each subcategory.
E.Total Products by  target audience(Donut Chart)
Donut chart shows count of targeted audience with percentage of total.

6. KPI Summary-
KPI           	Value	       Interpretation
Total products	5660	   Total products available
Average Rating	3.13	   Moderate customer satisfaction
Distinct Brands	754	     Different  brands for all categories
Max Price	      1000	      Maximum price
Min Price	      997	     Minimum price
High Rated %	  0.50	    Rating percentage

6.Insights-
Products are highly discounted (≈69%) and low-priced. Customer satisfaction is moderate (3.13), suggesting that while discounts attract customers, product quality or experience needs improvement.

7. Tools Used-
- Power BI Desktop for data visualization and dashboard creation
- Excel for initial data exploration
- DAX for KPI calculations
- Power Query Editor for data transformation
- 
8. Conclusion-
The analysis highlights that Snapdeal focuses on affordable, highly discounted products. While this attracts price-sensitive customers, moderate ratings suggest scope for improving product quality and service. Balancing discounting with quality enhancement will help improve both customer satisfaction and profitability.
