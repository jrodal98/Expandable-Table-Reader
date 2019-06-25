from table import read_paginated_table

# Simple example where the table's selectors are not dynamic
simple_df = read_paginated_table(
    "https://cavdailyonline.github.io/facultysalarygryphon/", 
    '#data-table-container',
    '#data-table-container_wrapper > div.dataTables_paginate.paging_bootstrap.pagination > ul > li.next > a',
    show_more_option='#data-table-container_length > label > select > option:nth-child(4)',
    delay=0)
simple_df.to_csv("simple_salary.csv",index=False)

# Difficult example where the table's selectors are dynamic and cannot be known
# until the webdriver is launched.  Additionally, the navigation bar changes upon navigating to
# the second page because a previous page button is added.  Thus, to sucessfully scrape
#  this table, you will need to do the following:
# 1) call read_paginated_table with no selectors specified
# 2) Input table selector and next button selector
# 3) go to page 2 and get the second page next button selector
# 4) go back to page 1
# 5) Hit enter
difficult_df = read_paginated_table(
    "https://b6.caspio.com/dp/d32d20002ac5f1b7da3046c89373",
     delay=.05)



