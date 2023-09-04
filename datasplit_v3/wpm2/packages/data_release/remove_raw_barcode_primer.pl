#!/usr/bin/perl -w

use strict;
use FindBin qw/$Bin/;
use Getopt::Long;

my %opts;
GetOptions (\%opts,"r1=s","r2=s","f=s","m=s","o=s");

my $usage = <<"USAGE";
        Program : $0
        Discription: remove barcode and primer of raw reads
        Usage:perl $0 [options]
                -r1   R1.fq
                -r2   R2.fq
                -f    split.config
	        -m    cut mode, barcode or primer
		-o    output directory 
USAGE

die $usage if (!$opts{f}) or (!$opts{r1}) or (!$opts{r2});
$opts{m}=$opts{m}?$opts{m}:"barcode";
$opts{o}=$opts{o}?$opts{o}:"./";

my $fq1=$opts{r1};
my $fq2=$opts{r2};
my $splitConfig=$opts{f};
my $mode=$opts{m};
my $outDir=$opts{o};


if($fq1 =~ /gz$/){
	open INF1,"gzip -dc $fq1 |" or die "$!\n";
}else{
	open INF1,$fq1 or die "$!\n";
}
if($fq2 =~ /gz$/){
	open INF2,"gzip -dc $fq2 |" or die "$!\n";
}else{
	open INF2,$fq2 or die "$!\n";
}


my (%sample,%Fbarcode,%Rbarcode);
open INL,$splitConfig or die "$!\n";
while(<INL>){
	chomp;
	next if(/^#/);
	my @temp = split;
	$sample{$temp[0]} = 1;
	$Fbarcode{$temp[1]} = $temp[2];
	$Rbarcode{$temp[3]} = $temp[4];
}
close INL;

my @temp1 = split(/\//,$fq1);
my @temp2 = split(/\//,$fq2);
if($mode eq "barcode"){
    open OUT1,"> $outDir/nobar.$temp1[-1]" or die "$!\n";
    open OUT2,"> $outDir/nobar.$temp2[-1]" or die "$!\n";
}elsif($mode eq "primer"){
    open OUT1,"> $outDir/noprimer.$temp1[-1]" or die "$!\n";
    open OUT2,"> $outDir/noprimer.$temp2[-1]" or die "$!\n";
}
#open OUT3,"> $outDir/discard.$temp1[-1]" or die "$!\n";
#open OUT4,"> $outDir/discard.$temp2[-1]" or die "$!\n";

my($tag1,$tag2);
while(<INF1>){
	chomp;
	chomp(my $seq1 = <INF1>);
	chomp(my $direction1 = <INF1>);
	chomp(my $quality1 = <INF1>);
	chomp(my $head2 = <INF2>);
	chomp(my $seq2 = <INF2>);
	chomp(my $direction2 = <INF2>);
	chomp(my $quality2 = <INF2>);
	foreach my $fb(keys %Fbarcode){
	    if($seq1=~/^$fb/){
		    $tag1 = 1;
		    my $sub_seq1 = substr($seq1,length($fb));
		    my $sub_quality1 = substr($quality1,length($fb));
		    if($mode eq "primer"){
		        $sub_seq1 = substr($sub_seq1,length($Fbarcode{$fb}));
			$sub_quality1 = substr($sub_quality1,length($Fbarcode{$fb}));
		    }
		    print OUT1 "$_\n$sub_seq1\n$direction1\n$sub_quality1\n";
		}elsif($seq2=~/^$fb/){
		    $tag2 = 1;
		    my $sub_seq2 = substr($seq2,length($fb));
		    my $sub_quality2 = substr($quality2,length($fb));
		    if($mode eq "primer"){
		        $sub_seq2 = substr($sub_seq2,length($Fbarcode{$fb}));
			$sub_quality2 = substr($sub_quality2,length($Fbarcode{$fb}));
		    }
		    print OUT1 "$head2\n$sub_seq2\n$direction2\n$sub_quality2\n";
		}
	}
	foreach my $rb(keys %Rbarcode){
	    if($seq2=~/^$rb/){
		    $tag2 = 1;
		    my $sub_seq2 = substr($seq2,length($rb));
		    my $sub_quality2 = substr($quality2,length($rb));
		    if($mode eq "primer"){
		        $sub_seq2 = substr($sub_seq2,length($Rbarcode{$rb}));
			$sub_quality2 = substr($sub_quality2,length($Rbarcode{$rb}));
		    }
		    print OUT2 "$head2\n$sub_seq2\n$direction2\n$sub_quality2\n";
		}elsif($seq1=~/^$rb/){
		    $tag1 = 1;
		    my $sub_seq1 = substr($seq1,length($rb));
		    my $sub_quality1 = substr($quality1,length($rb));
		    if($mode eq "primer"){
		        $sub_seq1 = substr($sub_seq1,length($Rbarcode{$rb}));
			$sub_quality1 = substr($sub_quality1,length($Rbarcode{$rb}));
		    }
		    print OUT2 "$_\n$sub_seq1\n$direction1\n$sub_quality1\n";
		}
	}
	if($tag1!=1){
	    print "F-barcode does not match!\n";
	    #print OUT3 "$_\n$seq1\n$direction1\n$quality1\n";
	}
	if($tag2!=1){
	    print "R-barcode does not match!\n";
	    #print OUT4 "$head2\n$seq2\n$direction2\n$quality2\n";
	}
}
close INF1;
close INF2;
close OUT1;
close OUT2;
#close OUT3;
#close OUT4;
