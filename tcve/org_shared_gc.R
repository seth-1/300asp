require("ggplot2")
require("reshape")
require("gplots")
require("RColorBrewer")
require("argparse")

args <- commandArgs(TRUE)
infile <- args[1]
description <- args[2:4] # Contains section, cutoff1 and cutoff 2

tmpdat=read.csv(infile, header = FALSE)
#subdat <- subset(tmpdat, tmpdat$V8=="Nigri" & tmpdat$V9=="Nigri", select=c(3,4,10))
subdat <- subdat[order(subdat$V1, subdat$V2), ]

#x <- barplot(as.matrix(tmpdat$V10), xaxt='n' , ylab= "Number of best hits inside one gene cluster", main='Distribution of gc-members throughout different genomes', sub='Gene Cluster (clust_id: 22_1079950_32)')
#text(cex=.6, x=x-1, y=-2, names(tmpdat) , xpd=TRUE, srt=45) # for rotated x-labels, put xaxt='n' into plot when in use!


#qplot(tmpdat$V10, ..density.., data=tmpdat, geom="density", fill=tmpdat$V3, position="stack")

pdf('density_orgs.pdf')
m<- ggplot(subdat, aes(x=subdat$V3))
p<- m + geom_density(aes(fill=factor(subdat$V1)), size=2, alpha=0.3) #+ coord_cartesian(xlim=c(0, 20))
print(p)
dev.off()

dat <- cast(tmpdat, V1~V2)

mat <- data.matrix(dat)
rownames(mat) <- dat[,1]
mat <- mat[,-1]

#my_palette <- colorRampPalette(c("yellow", "red"))(n = 1000) # for costum colors

pdf('map_orgs.pdf')
heatmap.2(mat,
        main = paste0("HM of section",description[1], "and cutoffs", description[2], description[3])
        dendrogram="none",
        trace = "none",
        na.color ="white",
        col=brewer.pal(7, "YlOrRd"),
        Rowv=NA,
        Colv=NA)
dev.off()