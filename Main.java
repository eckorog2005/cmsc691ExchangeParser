package com.company;

import org.gephi.data.attributes.api.*;
import org.gephi.graph.api.*;
import org.gephi.io.exporter.api.ExportController;
import org.gephi.io.exporter.spi.GraphExporter;
import org.gephi.io.importer.api.Container;
import org.gephi.io.importer.api.EdgeDefault;
import org.gephi.io.importer.api.ImportController;
import org.gephi.io.processor.plugin.DefaultProcessor;
import org.gephi.project.api.ProjectController;
import org.gephi.project.api.Workspace;
import org.gephi.statistics.plugin.ConnectedComponents;
import org.gephi.statistics.plugin.Modularity;
import org.openide.util.Lookup;

import java.io.File;
import java.io.IOException;
import java.math.BigDecimal;

public class Main {

    public static void main(String[] args) {

        double n = 100.0;
        BigDecimal alpha = new BigDecimal(.32);
        BigDecimal alpha2 = new BigDecimal(.62000);
        BigDecimal alpha3 = new BigDecimal(1);
        BigDecimal fraction = new BigDecimal(1.0/n);

        //Init a project - and therefore a workspace
        ProjectController pc = Lookup.getDefault().lookup(ProjectController.class);
        pc.newProject();
        Workspace workspace = pc.getCurrentWorkspace();

        //Get controllers and models
        ImportController importController = Lookup.getDefault().lookup(ImportController.class);
        GraphModel graphModel = Lookup.getDefault().lookup(GraphController.class).getModel();
        AttributeModel attributeModel = Lookup.getDefault().lookup(AttributeController.class).getModel();

        //Import file
        Container container;
        try {
            File file = new File("test.graphml");
            container = importController.importFile(file);
            container.getLoader().setEdgeDefault(EdgeDefault.DIRECTED);   //Force DIRECTED
        } catch (Exception ex) {
            ex.printStackTrace();
            return;
        }

        //Append imported data to GraphAPI
        importController.process(container, new DefaultProcessor(), workspace);

        //See if graph is well imported
        DirectedGraph graph = graphModel.getDirectedGraph();
        System.out.println("Nodes: " + graph.getNodeCount());
        System.out.println("Edges: " + graph.getEdgeCount());

        attributeModel.getEdgeTable().addColumn("edgeInCommunity", "edgeInCommunity", AttributeType.BIGDECIMAL,
                AttributeOrigin.DATA, BigDecimal.ZERO);

        for (int i = 0; i < n; i++) {

            //Run modularity algorithm - community detection
            System.out.println("i = "+i);
            Modularity modularity = new Modularity();
            modularity.setUseWeight(false);
            modularity.setRandom(false);
            modularity.execute(graphModel, attributeModel);

            //Partition with 'modularity_class', just created by Modularity algorithm
            for(Edge edge : graph.getEdges().toArray()){
                if(edge.getSource().getAttributes().getValue(Modularity.MODULARITY_CLASS).equals(
                        edge.getTarget().getAttributes().getValue(Modularity.MODULARITY_CLASS))){
                    BigDecimal communityCount = (BigDecimal) edge.getAttributes().getValue("edgeInCommunity");
                    if (communityCount == null) {
                        communityCount = BigDecimal.ZERO;
                    }
                    communityCount = communityCount.add(fraction);
                    edge.getAttributes().setValue("edgeInCommunity", communityCount);
                }
            }
        }

        findCCandOutput(graphModel,alpha,attributeModel,workspace);
        findCCandOutput(graphModel,alpha2,attributeModel,workspace);
        findCCandOutput(graphModel,alpha3,attributeModel,workspace);
    }

    public static void findCCandOutput(GraphModel graphModel, BigDecimal alpha, AttributeModel attributeModel,
                                  Workspace workspace){
        //new directed graph to make connected components
        GraphView view = graphModel.newView();
        DirectedGraph graph2 = graphModel.getDirectedGraph(view);

        System.out.println("Nodes: " + graph2.getNodeCount());
        System.out.println("Edges: " + graph2.getEdgeCount());

        for(Edge edge : graph2.getEdges().toArray()){
            BigDecimal communityCount = (BigDecimal) edge.getAttributes().getValue("edgeInCommunity");
            if(communityCount != null){
                if(communityCount.compareTo(alpha) < 0){
                    graph2.removeEdge(edge);
                }
            }else{
                if(alpha.compareTo(BigDecimal.ZERO) != 0){
                    graph2.removeEdge(edge);
                }
            }
        }

        System.out.println("Nodes: " + graph2.getNodeCount());
        System.out.println("Edges: " + graph2.getEdgeCount());

        //get connected components of new view
        graphModel.setVisibleView(view);
        ConnectedComponents cc = new ConnectedComponents();
        cc.setDirected(true);
        cc.execute(graphModel,attributeModel);

        //write graphml file
        ExportController ec = Lookup.getDefault().lookup(ExportController.class);
        //Export only visible graph
        GraphExporter exporter = (GraphExporter) ec.getExporter("gexf");     //Get GEXF exporter
        //graphModel.setVisibleView(printView);
        //exporter.setExportVisible(true);  //Only exports the visible (filtered) graph
        exporter.setWorkspace(workspace);
        try {
            String alphaName = alpha.toPlainString();
            if(alphaName.length() > 10){
                alphaName = alphaName.substring(0,10);
            }
            ec.exportFile(new File("acore"+alphaName+".gexf"), exporter);
        } catch (IOException ex) {
            ex.printStackTrace();
            return;
        }
    }
}
