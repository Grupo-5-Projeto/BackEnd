package school.sptech.menor_tempo_atendimento.service.grafo;

import com.fasterxml.jackson.databind.JsonNode;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import school.sptech.menor_tempo_atendimento.service.grafo.GrafoService;
import school.sptech.menor_tempo_atendimento.service.upa.UpaService;
import school.sptech.menor_tempo_atendimento.util.Nivel;
import school.sptech.menor_tempo_atendimento.util.NoGrafo;
import school.sptech.menor_tempo_atendimento.util.Par;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Component
public class GrafoFactory {

    @Autowired
    private GrafoService grafoService;
    @Autowired
    private UpaService upaService;
    private HashMap<String, List<Par<String, Integer>>> valorArestaTransporteUpa = new HashMap<>();


    //Metodo para pegar o JSON (API do Maps) e transformar em um HashMap
    //Estou utilizando JsonNode pois achei mais facil de manipular e
    // chegar no resultado final de um NoGrafo
    //Acredito que não é necessário criar classes para cada UPA e Meio de Transporte
    //pois não utilizariamos para mais nada alem de fazer a conversão para NoGrafo
    private HashMap<String, List<Par<String, Integer>>> jsonToHashMap(JsonNode upasProximas) {
        valorArestaTransporteUpa.clear();
        JsonNode upas = upasProximas.get("upas_proximas");
        for (JsonNode upa : upas) {
            String nome = upa.get("nome").asText();
            valorArestaTransporteUpa.putIfAbsent(nome, new ArrayList<>());
            JsonNode modos = upa.get("rotas");
            modos.fields().forEachRemaining(entry -> {
                String transporte = entry.getKey();
                String tempo = entry.getValue().get("Tempo Estimado").asText();

                valorArestaTransporteUpa.get(nome).add(new Par(transporte, Integer.parseInt(tempo.replaceAll("[^0-9]", ""))));
            });
        }

        return valorArestaTransporteUpa;
    }

    //Metodo para os valores do hashMap e adicionar em uma lista de NoGrafo
    //Para depois apenas adicionar os valores do grafo
    private List<NoGrafo> hashMapToNografo() {
        List<NoGrafo> listaAdicionarValoresGrafo = new ArrayList<>();
        int contador = 0;
        for (Map.Entry<String, List<Par<String, Integer>>> entry : valorArestaTransporteUpa.entrySet()) {
            String upa = entry.getKey();
            List<Par<String, Integer>> transporteTempo = entry.getValue();
            listaAdicionarValoresGrafo.add(new NoGrafo(upa, Nivel.NIVEL_UPA, 0));
            if (contador == 0) {
                for (Par<String, Integer> meioDeTransporteDaVez : transporteTempo) {
                    listaAdicionarValoresGrafo.add(new NoGrafo(meioDeTransporteDaVez.getChave(), Nivel.NIVEL_MEIO_DE_TRANSPORTE, 0));
                }
            }
            contador++;
        }

        return listaAdicionarValoresGrafo;
    }

    public GrafoBuilder factory(JsonNode jsonNode){
        jsonToHashMap(jsonNode);
        hashMapToNografo();
        return new GrafoBuilder(hashMapToNografo(),valorArestaTransporteUpa,grafoService,upaService);
    }
}

