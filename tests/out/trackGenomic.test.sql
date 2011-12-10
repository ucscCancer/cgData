DELETE from raDb where name = 'genomic_test';
INSERT into raDb( name, sampleTable, clinicalTable, columnTable, aliasTable, shortLabel, longLabel, expCount, dataType, platform, profile, security, priority, gain, groupName, wrangler, url, article_title, citation, author_list, wrangling_procedure) VALUES ( 'genomic_test', 'sample_test', 'clinical_test', 'colDb', 'genomic_test_alias', 'test1', 'test One', '5', 'bed 15', 'expression', 'localDb', 'public', 1.000000, 1.250000, 'test1 group', 'Chris Szeto', 'http://url.com', 'test1 article title', 'track cite', \N, \N);
drop table if exists sample_test;
CREATE TABLE sample_test (
    id           int,
    sampleName   varchar(255)
) engine 'MyISAM';
INSERT INTO sample_test VALUES( 0, '1' );
INSERT INTO sample_test VALUES( 1, '101' );
INSERT INTO sample_test VALUES( 2, '17' );
INSERT INTO sample_test VALUES( 3, '4' );
INSERT INTO sample_test VALUES( 4, 'sample63' );
drop table if exists genomic_test_alias;
CREATE TABLE genomic_test_alias (
    name        varchar(255),
    alias         varchar(255)
) engine 'MyISAM';
insert into genomic_test_alias( name, alias ) values( 'probe1', 'geneA' );
drop table if exists genomic_test;
CREATE TABLE genomic_test_tmp (
    id int unsigned not null primary key auto_increment,
    chrom varchar(255) not null,
    chromStart int unsigned not null,
    chromEnd int unsigned not null,
    name varchar(255) not null,
    score int not null,
    strand char(1) not null,
    thickStart int unsigned not null,
    thickEnd int unsigned not null,
    reserved int unsigned  not null,
    blockCount int unsigned not null,
    blockSizes longblob not null,
    chromStarts longblob not null,
    expCount int unsigned not null,
    expIds longblob not null,
    expScores longblob not null,
    INDEX(name(16)),
    INDEX(chrom(5),id)
) engine 'MyISAM';
insert into genomic_test_tmp(chrom, chromStart, chromEnd, strand,  name, expCount, expIds, expScores) values ( 'chrX', '1', '10', '+', 'probe1', '5', '0,1,2,3,4', '0.47900506515,-1.23,5.3,25.1,3.1' );
# sort file by chrom position
create table genomic_test like genomic_test_tmp;
insert into genomic_test select * from genomic_test_tmp order by chrom, chromStart;
drop table genomic_test_tmp;
