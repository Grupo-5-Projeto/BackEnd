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
        List<NoGrafo> listaUpas = listarUpas(grafo);
        Map<NoGrafo, NoGrafo> rotaAtendimento = getRotaAtendimento(grafo);
        Map<NoGrafo, Double> tempos = dijkstra.algoritmoDijkstra(grafo);
        return dijkstra.caminhoOtimizado(tempos,listaUpas, rotaAtendimento, grafo);
    }

    private List<NoGrafo> listarUpas(Map<NoGrafo, List<Par<NoGrafo, Double>>> grafo){
        List<NoGrafo> listaUpas = new ArrayList<>();
        Map<NoGrafo, NoGrafo> rotaMedicos = new HashMap<>();
        for (NoGrafo noDaVez : grafo.keySet()) {
            if (noDaVez.getNivel() == Nivel.NIVEL_UPA) {
                listaUpas.add(noDaVez);
            }
            if (noDaVez.getNivel() == Nivel.NIVEL_TEMPO_DE_ESPERA) {
                for (NoGrafo vizinho : grafo.keySet()) {
                    if (noDaVez.getNivel() == Nivel.NIVEL_UPA) {
                        rotaMedicos.put(vizinho, noDaVez);
                    }
                }

            }
        }
        return listaUpas;
    }

    private Map<NoGrafo, NoGrafo> getRotaAtendimento(Map<NoGrafo, List<Par<NoGrafo, Double>>> grafo){
        Map<NoGrafo, NoGrafo> rotaMedicos = new HashMap<>();
        for (NoGrafo noDaVez : grafo.keySet()) {
            if (noDaVez.getNivel() == Nivel.NIVEL_TEMPO_DE_ESPERA) {
                for (NoGrafo vizinho : grafo.keySet()) {
                    if (vizinho.getNivel() == Nivel.NIVEL_UPA) {
                        if (noDaVez.getNome().equals(vizinho.getNome() + "-" + "tempoEspera")) {
                            rotaMedicos.put(vizinho, noDaVez);
                        }
                    }
                }

            }
        }
        return rotaMedicos;
    }
}