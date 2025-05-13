## mmseqs2 for protein and lncrna fasta
## MMseqs2 Version: 13.45111 under base env

WD='/home/user_li/linqin_tmp/Dataset/cluster_mmseqs2'
cd $WD

if [[ -d $WD/out ]]; then
	echo $WD/out exit!
else
	mkdir $WD/out
fi

cd $WD/out


for line in $( ls $WD | grep "lineBreak" | sed 's/[.]fa.*//g' )
do
	if [[ $line =~ "UP" ]]; then
		mmseqs easy-cluster -v 1 --min-seq-id 0.5 -c 0.8 --cov-mode 1 --cluster-mode 2  $WD/$line".fa" $line tmp	# -min-seq-id 0.5 -c 0.8 for proteins	
	else
		mmseqs easy-cluster -v 1 --min-seq-id 0.7 -c 0.8 --cov-mode 1 --cluster-mode 2  $WD/$line".fa" $line tmp	# -min-seq-id 0.7 -c 0.8 for RNAs
	fi

	echo $line done!
done
