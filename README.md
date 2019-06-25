# Paginated-Table-Extractor
A python script that automates the extraction of data from paginated tables.

![](simple.gif)

The above gif shows a table with 10,678 instances over 108 pages being extracted into a pandas dataframe in less than 10 seconds.  This was the code that produced that result:

```python
simple_df = read_paginated_table(
    "https://cavdailyonline.github.io/facultysalarygryphon/", 
    '#data-table-container',
    '#data-table-container_wrapper > div.dataTables_paginate.paging_bootstrap.pagination > ul > li.next > a',
    show_more_option='#data-table-container_length > label > select > option:nth-child(4)',
    delay=0)
```

## Download instructions
1) Clone this repository.
```bash
git clone https://github.com/jrodal98/Paginated-Table-Extractor.git
```
2) Install python dependencies.  Something similar to this should do the job.
```bash
cd Paginated-Table-Extractor
pip3 install -r requirements.txt
```
3) Install chromedriver [here](http://chromedriver.chromium.org/downloads).  Depending on your operating system, you might have to add it to your path, which is left as an exercise to the reader.  If the script complains about not being able to find the driver but you installed it, then you need to add it to your path. 

4) **optional**: Run test.py to make sure that everything is working properly and to get a feel for how to use the script.

