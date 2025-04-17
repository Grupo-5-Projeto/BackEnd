package school.sptech.menor_tempo_atendimento;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import school.sptech.menor_tempo_atendimento.service.GrafoService;

import java.io.IOException;


public class Main {
        public static void main(String[] args) throws IOException {

            String json = "{ \"upas_proximas\": [ { \"nome\": \"UPA MASATAKA OTA\", \"modos_transporte\": { \"Carro\": { \"Distância\": \"14.05 km\", \"Tempo Estimado\": \"41 min\" }, \"Moto\": { \"Distância\": \"14.05 km\", \"Tempo Estimado\": \"29 min\" }, \"Transporte Público\": { \"Distância\": \"23.77 km\", \"Tempo Estimado\": \"97 min\" }, \"A Pé\": { \"Distância\": \"12.74 km\", \"Tempo Estimado\": \"180 min\" } } }, { \"nome\": \"UPA 26 DE AGOSTO\", \"modos_transporte\": { \"Carro\": { \"Distância\": \"18.29 km\", \"Tempo Estimado\": \"54 min\" }, \"Moto\": { \"Distância\": \"18.29 km\", \"Tempo Estimado\": \"37 min\" }, \"Transporte Público\": { \"Distância\": \"25.39 km\", \"Tempo Estimado\": \"88 min\" }, \"A Pé\": { \"Distância\": \"16.45 km\", \"Tempo Estimado\": \"231 min\" } } }, { \"nome\": \"UPA CIDADE TIRADENTES\", \"modos_transporte\": { \"Carro\": { \"Distância\": \"53.31 km\", \"Tempo Estimado\": \"60 min\" }, \"Moto\": { \"Distância\": \"28.87 km\", \"Tempo Estimado\": \"39 min\" }, \"Transporte Público\": { \"Distância\": \"42.13 km\", \"Tempo Estimado\": \"113 min\" }, \"A Pé\": { \"Distância\": \"20.33 km\", \"Tempo Estimado\": \"290 min\" } } } ] }";

            ObjectMapper mapper = new ObjectMapper();
            JsonNode root = mapper.readTree(json);

            GrafoService grafoService = new GrafoService();
            grafoService.jsonToHashMap(root);
            grafoService.gerarNosGrafo(grafoService.hashMapToNografo());
            grafoService.gerarArestasGrafo();
            grafoService.caminhoOtimizado(grafoService.algoritmoDijkstra());
        }
    }

