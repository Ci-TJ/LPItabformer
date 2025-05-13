### env base or NGS!


echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ $(date)~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ $(date)~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

##0 Setting work directory and download files
#Setting directory
echo ==================================================== Mouse ====================================================
echo ==================================================== Mouse ====================================================

WD=/home/user_li/linqin_tmp/Dataset/BioGram/compare/pj231220/   #Make sure your work directory
methD=/home/user_li/linqin_tmp/Dataset/BioGram/compare/test/MathFeature-master/methods

faWD=/home/user_li/linqin_tmp/Dataset/cluster_mmseqs2/


cd $WD

#Preparation
if [[ -d $WD/sequence ]]; then
	echo $WD/sequence exit! 
else
	mkdir $WD/sequence
fi

if [[ -d $WD/feature ]]; then
	echo $WD/feature exit! 
else
	mkdir $WD/feature
fi

grep ">" $faWD/gencode.vM28.lncRNA_transcripts_lineBreak.fa | sed "s/>//g" | sort -n | uniq >  muniqR
grep ">" $faWD/UP000000589_55315_uniprot-compressed_true_download_true_format_fasta_includeIsoform_tr-2022.08.26-05.39.55.36_lineBreak.fa | sed "s/>//g" | sort -n | uniq > muniqP

## Retrieve the RNA sequences
# Note: '1~2!s/T/U/g' and sed '0~2s/T/U/g', couldn't use [sed '1~2!s/.*/\U&/g']
if [[ -f $WD/sequence/gencode.vM28_lncrna_seq.fa ]]; then
	echo $WD/sequence/gencode.vM28_lncrna_seq.fa OK!
else
	echo $WD/sequence/gencode.vM28_lncrna_seq.fa Not exit!
	for line in $(cat $WD/muniqR)
	do
		grep -A 1 $line $faWD/gencode.vM28.lncRNA_transcripts_lineBreak.fa | sed '0~2s/.*/\U&/g' | sed '0~2s/T/U/g' | sed "0~2s/[^AUGC]//g" >> $WD/sequence/gencode.vM28_lncrna_seq.fa || echo $line fail!
	done
fi
#sed -i '1~2!s/T/U/g' $WD/sequence/hEVLncRNAsV2_rna_seq.fa

## Retrieve the protein sequences
#ACDEFGHIKLMNPQRSTVWY, no BOXJUZ
if [[ -f $WD/sequence/UP000000589_55315_uniprot_mus_prot_seq.fa ]]; then
	echo $WD/sequence/UP000000589_55315_uniprot_mus_prot_seq.fa OK!
else
	echo $WD/sequence/UP000000589_55315_uniprot_mus_prot_seq.fa Not exit!
	for line in $(cat $WD/muniqP)
	do
		# "$" make sure for right isoform
		grep -A 1 $line"$" $faWD/UP000000589_55315_uniprot-compressed_true_download_true_format_fasta_includeIsoform_tr-2022.08.26-05.39.55.36_lineBreak.fa | sed '0~2s/.*/\U&/g' | \
			sed "0~2s/[^ACDEFGHIKLMNPQRSTVWY]//g" >> $WD/sequence/UP000000589_55315_uniprot_mus_prot_seq.fa || echo $line fail!
	done
fi

######################################################
#sed '/^>/!s/T/U/g'
#cat $faWD/gencode.v39.lncRNA_transcripts_lineBreak_all_seqs.fasta |  sed '0~2s/.*/\U&/g' | sed '0~2s/T/U/g' | sed "0~2s/[^AUGC]//g" > $WD/sequence/gencode.v39_lncrna_seq.fa || echo sed RNAs fail! #T need to convert to U
#cat $faWD/UP000005640_79740_uniprot_hsa_iden0.5_all_seqs.fasta |  sed '0~2s/.*/\U&/g' | sed "0~2s/[^ACDEFGHIKLMNPQRSTVWY]//g"> $WD/sequence/UP000005640_79740_uniprot_hsa_prot_seq.fa || echo sed proteins fail!

#cat $faWD/gencode.v39.lncRNA_transcripts_lineBreak_all_seqs.fasta |  sed '/^>/!s/.*/\U&/g' | sed '/^>/!s/T/U/g' | sed '/^>/!s/[^AUGC]//g' > $WD/sequence/gencode.v39_lncrna_seq.fa || echo sed RNAs fail! #T need to convert to U
#cat $faWD/UP000005640_79740_uniprot_hsa_iden0.5_all_seqs.fasta |  sed '/^>/!s/.*/\U&/g' | sed '/^>/!s/[^ACDEFGHIKLMNPQRSTVWY]//g'> $WD/sequence/UP000005640_79740_uniprot_hsa_prot_seq.fa || echo sed proteins fail!
######################################################

echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ $(date)~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ $(date)~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


out1=3mer_gencode.vM28_lncrna_mus.csv
out2=1mer_UP000000589_prot_mus.csv

if [[ -d $WD/feature ]]; then
	echo $WD/feature exit! 
else
	echo $WD/feature && mkdir $WD/feature
fi


#lncRNA 3mer
if [[ -f $WD/feature/$out1 ]]; then
	echo $WD/feature/$out1 exit! 
else
	echo $WD/feature/$out1 Not exit!
	python3 $methD/ExtractionTechniques.py -i $WD/sequence/gencode.vM28_lncrna_seq.fa -o $WD/feature/$out1 -l RNA -t TNC -seq 2  && echo $out1 OK! # -seq 1 for DNA and 2 for RNA, -l just for label, could be anyone
fi

#protein 1mer
if [[ -f $WD/feature/$out2 ]]; then
	echo $WD/feature/$out2 exit! 
else
	echo $WD/feature/$out2 Not exit!
	python3 $methD/ExtractionTechniques-Protein.py -i $WD/sequence/UP000000589_55315_uniprot_mus_prot_seq.fa -o $WD/feature/$out2 -l Protein -t AAC  && echo $out2 OK! # -l just for label, could be anyone
fi

echo ALL Done!
echo ====================================================== $(date) ======================================================
echo ====================================================== $(date) ======================================================


