# Search-Engine
A Search Engine built from scratch on the Wikipedia data dump.

**Name:** Hitesh Goel
**Roll Num:** 2020115003

### Project Objective
In this project, primary task is to build a scalable and efficient search engine on Wikipedia pages. This constitutes two stages - inverted index creation and query search mechanism, where the scope of performance in the second stage relies heavily on the quality of index built in its preceding stage. Throughout the project, efforts have been made to build a system optimized for search time, search efficiency (i.e. the quality of results), indexing time and index size. We have used Wikipedia dumps of size over 90 GB in XML format, which is parsed to get Wikipedia pages.

### Directory structure
- main
    - src
        - indexer.py
        - merger.py
        - secondary.py
        - search.py
        - index.sh
        - search.sh
        - hindi_indexer.py
        - hindi_merge_index.py
        - hindi_secondary.py
        - hindi_search.py
        - hindi_stopwords.txt
        - hindi_stemwords.txt
        - hindi_search.sh
        - stats.txt
    - README.md

### Basic Stages
- XML Parsing (SAX parser): Need to parse each page , title tag, infobox, body , category etc..
- Tokenization: Tokenize sentense to get each token using regex
- Case folding: make it all to lowercase
- Stop words removal: remove stop word which are more frequently occured in a sentences (downloaded from nltk)
- Stemming (using Porter Stemmer): get root/base word and store it
- Posting list / inverted index creation: create word & its positing list
- Optimization: HTML entities and links were also removed from the files, which helped in reducing the size significantly. Words with length greater than 45 were removed during creation of primary index and numbers with length greater than 10 were removed during creation of secondary index. The posting list is also stored in a way so as to minimise space.

Another technique used to reduxe search time is the creation of a secondary index over the primary index.

Sample Posting List:

```
latvia:d465741b1 d467407b1 d468293b1 d469429b1 d471617b1 d471885b9c1 d472579b1 d472623b3 d475465b1
laura: d467207b1 d467220b2i2 d467445b1 d467627b1 d468059b1 d468317b2 d470622b1 d470806b1 d471262b1i2 d471264b1 d471569t1b1
```

Index size is less than 1/4th of the actual size of the dump.

### Features
 **Support for plain & field queries**
  Ensured support for both - plain and field queries. The expected fields from a Wikipedia page to be supported along with their respective identifiers used in query are as shown below in Table 1.
| FIELD | Title | Info | Category | Body | References | External Links |
| ------ | ------ |------ | ------ |------ | ------ |------ | 
| **SYMBOL** | t | i | c | b | r | l |

 **Plain query examples :** `Lionel Messi`, `Barcelona`
 **Field query examples :** `t:World Cup i:2018 c:Football` – search for ”World Cup” in Title, ”2018”
in Infobox and ”Football” in Category
 **Index size** is around one-fourth of the original dump size 

### Index Creation
For creating indexes use the following command : 
```
bash index.sh <path to data> <path to dir to store the index> <stats_indexer.txt>
```

### Merging the index
Once the index files have been created, we need to merge them into one large file. This is done by the algorithm to merge k-sorted arrays using a min-heap. 

To merge the index, run:
```
python3 merger.py
```
Creates the index in ../complete directory.

### Creating Secondary index
This is a further optimisation to our index that allows us to run a merge sort type algorithm while searching for queries.

```
python3 secondary.py
```

### Query Search
For each query string, it returns the top 10 results, each result consisting of the document id and title of the page.  The queries will be provided in a `queries.txt` file. It can be run as: 

```
bash search.sh
```

Code writes the search output for the given queries in a `queries_op.txt` file.
Change the arguments in the sh file in case of different file names.

**1. queries.txt**
This file given to you will contain each query string printed on a single line.
A dummy queries.txt:
~~~
t:World Cup i:2019 c:cricket
the two Towers
~~~
**2. queries_op.txt**
In this file, for each query, you will have the results printed on 10 lines, each line containing the document id (which is a number specific to your implementation) and title of the corresponding Wikipedia page. The title will be the original page title as contained in the XML dump.
**Dummy results for the above queries:**
~~~
7239, cricket world cup
4971952, 2019 cricket world cup
57253320, 2019 cricket world cup final
.
.
.
(10 lines of retrieved document id - title pairs)
5
63750, the two towers
173944, lord of the rings: the two towers
.
.
.
(10 lines of retrieved document id - title pairs)
2
~~~


### Challenges
- Difficult to process large data of 90 GB
- Can not store word & its posting list directly into a main memory, So Used K-way Merge sort
- Can not Load full final index into main memory, So Build Secondary Index on top of Primary Index (Posting List)