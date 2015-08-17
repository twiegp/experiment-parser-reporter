library(reshape2)
library(car)

format <- function(df.full) {
  # Not much formatting necessary for now!!
  df.full$Milk <- recode(df.full$Market_Price_Last_1,"-1=NA")
  df.full$Eggs<- recode(df.full$Market_Price_Last_2,"-1=NA")
  df.full$Sugar <- recode(df.full$Market_Price_Last_3,"-1=NA")
  
  assign("df_formatted", df.full, envir = .GlobalEnv) # Assign back for saving, if necessary.
}

make_objects <- function(df.merged) {
  
  uniqueIDs <- unique(df.merged$ID)
  
  df_python <- data.frame()
  
  
  # Generate a graph for each ID
  for (i in seq_along(uniqueIDs)) {
    thisID <- uniqueIDs[i]
    df <- df.merged[df.merged$ID == thisID,]
    
    # Get total Q exchanged
    transactions_1 <- df[df$Tick == max(df$Tick),"Market_Transactions_1"]
    transactions_2 <- df[df$Tick == max(df$Tick),"Market_Transactions_2"]
    transactions_3 <- df[df$Tick == max(df$Tick),"Market_Transactions_3"]
    
    # Get total Q supply
    players <- max(df$Players_N)
    supply_1 <- sum(df[df$Tick == max(df$Tick),unlist(lapply(c(1:players), FUN = function(x) paste("Subject",x,"Harvested_1",sep="_")))])
    supply_2 <- sum(df[df$Tick == max(df$Tick),unlist(lapply(c(1:players), FUN = function(x) paste("Subject",x,"Harvested_2",sep="_")))])
    supply_3 <- sum(df[df$Tick == max(df$Tick),unlist(lapply(c(1:players), FUN = function(x) paste("Subject",x,"Harvested_3",sep="_")))])
    
    
    df_melted <- melt(df, id.vars = c("Tick","ID","Order","Pool_Label"), measure.vars = c("Milk","Eggs","Sugar"))
    
    price_plot <- ggplot(df_melted, aes(x=Tick,y=value,color=variable)) + 
      geom_line() +
      labs(y="Price",x="Time",color="Prices") +
      stat_summary(fun.y = mean, geom="line", size=1.5) +
      scale_color_manual(values=c("blue","red","green")) +
      theme(axis.title.x = element_text(size=24),
            axis.text.x = element_text(size=20),
            axis.text.y = element_text(size=20),
            axis.title.y = element_text(size=24),
            legend.title = element_text(size=24),
            legend.text = element_text(size=20),
            strip.text = element_text(size=14)) +
      xlim(0,max(df_melted$Tick)) +
      ylim(0,NA)
    
    #price_plot <- linePlotWrapper(df_melted,"Tick","Time","value","Price","variable","Good", points=F, xrange = c(1:max(df_melted$Tick)), yrange = c(0:200))
    assign(paste("Prices",thisID,sep="_"), price_plot, envir = .GlobalEnv)
    
    new_row <- matrix(c(as.character(df$Pool_Label[1]),as.character(df$Order[1]),paste("Prices",thisID,sep="_"), transactions_1, transactions_2, transactions_3, supply_1, supply_2, supply_3), ncol=9)
    
    df_python <- rbind.fill(df_python, as.data.frame(new_row))
  }
  colnames(df_python) <- c("Label","Order","Plotname","Exchanged_1","Exchanged_2","Exchanged_3","Supply_1","Supply_2","Supply_3")
  write.table(df_python, file = "pipelineFiles\\slideInfo.csv", sep=",", row.names=F, quote=F)
  
}