linePlotWrapper <- function(df,xVar,xName,yVar,yName,treatmentVar,treatmentName,filename="",save=T,plot=F,startRound=1,points=T,xrange=F,yrange=F) {
  evalString1 <- paste("ggplot(data=df[df$Round>=startRound,],aes(x=",xVar,",y=",yVar,",color=",treatmentVar,"))",sep="")
  #evalString2 <- paste("geom_line(aes(color=",treatmentVar,"),size=1.5)",sep="")
  evalString3 <- paste("geom_point(aes(color=",treatmentVar,"))",sep="")
  if (points == F) { # Disabled right now, because it needs to be some way of blanking evalString3 without throwing an error and idk how to do that.
    evalString3 <- "labs(y=yName,x=xName,color=treatmentVar)"
  }
  print(evalString1)
  #print(evalString2)
  print(evalString3)
  plot <- eval(parse(text=evalString1)) +
    stat_summary(fun.y = mean, geom="line", size=1.5) +
    eval(parse(text=evalString3)) +
    labs(y=yName,x=xName,color=treatmentVar) +
    theme(axis.title.x = element_text(size=24),
          axis.text.x = element_text(size=20),
          axis.text.y = element_text(size=20),
          axis.title.y = element_text(size=24),
          legend.title = element_text(size=24),
          legend.text = element_text(size=20),
          strip.text = element_text(size=14))
  
  if (xrange != F) {
    plot <- plot + xlim(xrange[1],xrange[2])
  }
  
  if (yrange != F) {
    plot <- plot + ylim(yrange[1],yrange[2])
  }
  
  if (save == T && filename != "") {
    ggsave(plot,filename=filename,path=saveDir,width=12,height=9,limitsize=F)
  }
  #if (plot == T) {
  #  plot(plot)
  #}
  return(plot)
}


boxPlotWrapper <- function(df,xVar,xName,yVar,yName,filename="",save=T,plot=F,startRound=1,yrange=F) {
  evalString1 <- paste("ggplot(data=df[df$Round>=startRound,],aes(x=",xVar,",y=",yVar,"))",sep="")
  evalString2 <- paste("geom_boxplot(aes(fill=",xVar,"))",sep="")
  plot <- eval(parse(text=evalString1)) +
    eval(parse(text=evalString2)) +
    geom_jitter(position=position_jitter(width=.1)) +
    scale_fill_discrete(name=xName) +
    labs(y=yName,x=xName,color=xName) +
    theme(axis.title.x = element_text(size=24),
          axis.text.x = element_text(size=20),
          axis.text.y = element_text(size=20),
          axis.title.y = element_text(size=24),
          legend.title = element_text(size=24),
          legend.text = element_text(size=20),
          strip.text = element_text(size=14))
  
  
  if (yrange != F) {
    plot <- plot + ylim(yrange[1],yrange[2])
  }
  
  if (save == T && filename != "") {
    ggsave(plot,filename=filename,path=saveDir,width=12,height=9,limitsize=F)
  }
  return(plot)
}