package school.sptech.menor_tempo_atendimento.service.menorCaminhoAtendimento.impl;

import com.fasterxml.jackson.databind.JsonNode;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import school.sptech.menor_tempo_atendimento.domain.Dijkstra;
import school.sptech.menor_tempo_atendimento.dto.MelhorCaminho;
import school.sptech.menor_tempo_atendimento.service.grafo.GrafoFactory;
import school.sptech.menor_tempo_atendimento.service.menorCaminhoAtendimento.MenorCaminhoAtendimentoService;
import school.sptech.menor_tempo_atendimento.domain.Nivel;
import school.sptech.menor_tempo_atendimento.domain.NoGrafo;
import school.sptech.menor_tempo_atendimento.domain.Par;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class MenorCaminhoAtendimentoServiceImpl implements MenorCaminhoAtendimentoService {

    @Autowired
    private GrafoFactory grafoFactory;

    @Override
    public MelhorCaminho getMelhorCaminho(JsonNode jsonNode) {
        Dijkstra dijkstra = new Dijkstra();
        Map<NoGrafo, List<Par<NoGrafo, Double>>> grafo = grafoFactory.factory(jsonNode).build();
        List<NoGrafo> listaUpas = getListUpaTempoDeEspera(grafo);
        Map<NoGrafo, Double> tempos = dijkstra.algoritmoDijkstra(grafo);
        return dijkstra.caminhoOtimizado(tempos,listaUpas, grafo);
    }

    private List<NoGrafo> getListUpaTempoDeEspera(Map<NoGrafo, List<Par<NoGrafo, Double>>> grafo){
        List<NoGrafo> listaUpas = new ArrayList<>();
        for (NoGrafo noDaVez : grafo.keySet()) {
            if (noDaVez.getNivel() == Nivel.NIVEL_UPA) {
                listaUpas.add(noDaVez);
            }
        }
        return listaUpas;
    }


}