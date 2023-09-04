#!/usr/bin/perl -w
use strict;

my ($inputFq,$configF,$configR,$linkPrimer_th,$outPrefix);

my $opt;
while($opt = shift){
	if($opt eq "-i"){
		$inputFq = shift;
	}elsif($opt eq "-f"){
		$configF = shift;
	}elsif($opt eq "-r"){
		$configR = shift;
	}elsif($opt eq "-l"){
		$linkPrimer_th = shift;
	}elsif($opt eq "-o"){
		$outPrefix = shift;
	}elsif($opt eq "-h"){
		&usage();
		exit;
	}
}

unless($inputFq and $configF and $configR  and $outPrefix){
	&usage();
	exit;
}

$linkPrimer_th = 2 unless(defined($linkPrimer_th));

my %abbrev=(
    'A' => "AA",    'T' => "TT",
    'C' => "CC",    'G' => "GG",
    'M' => "AC",    'R' => "AG",
    'W' => "AT",    'S' => "CG",
    'Y' => "CT",    'K' => "GT",
    'V' => "ACG",    'H' => "ACT",
    'D' => "AGT",    'B' => "CGT",
    'X' => "ACGT",    'N' => "ACGT",
    'I' => "ACGT",
);

my $Fprimer=$configF;
my $Rprimer=$configR;
my $lenF = length($Fprimer);
my $lenR = length($Rprimer);


if($outPrefix =~ /_AA$/){
	#print("hehe\n");
	$outPrefix =~ s/_AA$//g;
	#open OUT,">> $outPrefix.split.fq" or die "$!\n";
	open OUT2,">> $outPrefix.split.primer.fq" or die "$!\n";
	open OUTM,"> $outPrefix.split.remove.fq" or die "$!\n";
}else{
	#open OUT,"> $outPrefix.split.fq" or die "$!\n";
	open OUT2,"> $outPrefix.split.primer.fq" or die "$!\n";
	open OUTM,">> $outPrefix.split.remove.fq" or die "$!\n";		
}

if($inputFq =~ /gz$/){
	open INR,"gzip -dc $inputFq |" or die "$!\n";
}else{
	open INR,$inputFq or die "$!\n";
}

my $sample_id;

while(<INR>){
	chomp;
	if($.%4==1){ $sample_id=$_}
	#chomp(my $sample_id = <INR>);
	chomp(my $seq = <INR>);
	chomp(my $direction = <INR>);
	chomp(my $quality = <INR>);
	#print ("$sample_id\n");
	my $seq2;
	my $quality2;
	my $seq22;
	my $quality22;
	my $Fprimer_mismatch2;
	my $Rprimer_mismatch2;
	for(my $j =0;$j <16;$j++){
		my $Fprimer_mismatch2=0;
		my $Rprimer_mismatch2=0;
		for(my $k = 0;$k < length($Fprimer);$k++){
			my $seq_base2 = substr($seq,$k+$j,1);
			my $Fprimer_base2 = substr($Fprimer,$k,1);
			$Fprimer_mismatch2++ unless($abbrev{$Fprimer_base2} =~ /$seq_base2/i);
			#print("$abbrev{$Fprimer_base2}\t$seq_base2\n");
		}
		for(my $k2 = 0;$k2 < length($Rprimer);$k2++){
			my $seq_base22 = substr($seq,$k2+$j,1);
			my $Rprimer_base2 = substr($Rprimer,$k2,1);
			$Rprimer_mismatch2++ unless($abbrev{$Rprimer_base2} =~ /$seq_base22/i);
		}
		$seq22 = substr($seq,$j);
		$quality22 = substr($quality,$j);
		if($Fprimer_mismatch2 <= $linkPrimer_th){
			#$seq2 = substr($seq,$j+$lenF);
			#$quality2 = substr($quality,$j+$lenF);
			#print OUT "$sample_id\n$seq2\n$direction\n$quality2\n";
			print OUT2 "$sample_id\n$seq22\n$direction\n$quality22\n";
			last;
		}
		if($Rprimer_mismatch2 <= $linkPrimer_th){
			#$seq2 = substr($seq,$j+$lenR);
			#$quality2 = substr($quality,$j+$lenR);
			#$seq2 = reverse $seq2;
            #$seq2 =~ tr/ATGC/TACG/;
			#$quality2 = reverse $quality2;
			#$quality2 =~ tr/ATGC/TACG/;
			$seq22 = reverse $seq22;
			$seq22 =~ tr/ATGC/TACG/;
			$quality22 = reverse $quality22;
			$quality22 =~ tr/ATGC/TACG/;
			#print OUT "$sample_id\n$seq2\n$direction\n$quality2\n";
			print OUT2 "$sample_id\n$seq22\n$direction\n$quality22\n";
			last;
		}	
		if($j==15){
			my $seq3;
			my $quality3;
			my $seq33;
			my $quality33;
			my $Fprimer_mismatch3;
			my $Rprimer_mismatch3;
			for(my $j3 =17;$j3 <=27;$j3++){
				my $m3 = $j3-1;
				my $m33 = $j3-1;
				my $Fprimer_mismatch3=0;
				my $Rprimer_mismatch3=0;
				for(my $k3 = length($Fprimer);$k3>=3 ;$k3--){
					my $n = $m3--;					
					my $seq_base3 = substr($seq,$n,1);
					my $Fprimer_base3 = substr($Fprimer,$k3-1,1);
					$Fprimer_mismatch3++ if($abbrev{$Fprimer_base3} =~ /$seq_base3/i);	
					
				}
				for(my $k33 = length($Rprimer);$k33>=3 ;$k33--){
					my $n3 = $m33--;
					my $seq_base33 = substr($seq,$n3,1);
					my $Rprimer_base3 = substr($Rprimer,$k33-1,1);
					$Rprimer_mismatch3++ if($abbrev{$Rprimer_base3} =~ /$seq_base33/i);
					#print "$abbrev{$Rprimer_base3}\t$seq_base33\n";
					#sleep(5);
				}
				if($j3>=23){
					$seq33 = substr($seq,$j3-20);
					$quality33 = substr($quality,$j3-20);
				}else{
					$seq33 = $seq;
					$quality33 = $quality;
				}
				
				if($Fprimer_mismatch3 >= 11){
					#print OUT "$sample_id\n$seq3\n$direction\n$quality3\n";
					print OUT2"$sample_id\n$seq33\n$direction\n$quality33\n";
					last;
				}
				if($Rprimer_mismatch3 >=11){
					$seq33 = reverse $seq33;
					$seq33 =~ tr/ATGC/TACG/;
					$quality33 = reverse $quality33;
					$quality33 =~ tr/ATGC/TACG/;
					#print OUT "$sample_id\n$seq3\n$direction\n$quality3\n";
					print OUT2"$sample_id\n$seq33\n$direction\n$quality33\n";
					last;


				}
				if($j3==27){
					print OUTM "$sample_id\n$seq\n$direction\n$quality\n";
				#	my $reverse_seq = reverse $seq;
				#	my $reverse_quality = reverse $quality;
				#	$reverse_seq =~ tr/ATGC/TACG/;
				#	print OUTM "$sample_id\n$reverse_seq\n$direction\n$reverse_quality\n";
				}
			}
		}
	}
	
	
           
}

close INR;
close OUT2;
#close OUT;
close OUTM;

sub usage{
print <<EOD
    
    Description: split sequences for each sample by barcode
    Version: V1.20140214
    Contact: hua.chen\@majorbio.com

    usage: perl $0 -i merge.fq -f Fprimer -r Rprimer -l linkPrimer.cutoff -o out.prefix
        -i  merged fastq file,required
        -f  F primer sequence
		-r  R primer sequence
        -l  link primer cutoff,default 2
        -o  output prefix,required
EOD
}
