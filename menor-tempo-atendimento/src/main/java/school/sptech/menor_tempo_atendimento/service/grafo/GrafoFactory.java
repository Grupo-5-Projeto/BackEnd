package school.sptech.menor_tempo_atendimento.service.grafo;

import com.fasterxml.jackson.databind.JsonNode;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Scope;
import org.springframework.stereotype.Component;
import school.sptech.menor_tempo_atendimento.service.upa.UpaService;
import school.sptech.menor_tempo_atendimento.domain.Nivel;
import school.sptech.menor_tempo_atendimento.domain.NoGrafo;
import school.sptech.menor_tempo_atendimento.domain.Par;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Component
public class GrafoFactory {

    @Autowired
    private UpaService upaService;

    //Map
    //Chave -> nome da upa
    //Valor -> lista de meio de transporte com seu nome e tempo até chegar na upa
    private HashMap<String, List<Par<String, Integer>>> mapearUpasESeusTransportes(JsonNode upasProximas) {
        HashMap<String, List<Par<String, Integer>>> mapUpaESeusTransportes = new HashMap<>();
        JsonNode upas = upasProximas.get("upas_proximas");
        for (JsonNode upa : upas) {
            String nome = upa.get("nome").asText();
            mapUpaESeusTransportes.putIfAbsent(nome, new ArrayList<>());
            JsonNode modos = upa.get("rotas");
            modos.fields().forEachRemaining(entry -> {
                String transporte = entry.getKey();
                String tempo = entry.getValue().get("Tempo Estimado").asText();

                mapUpaESeusTransportes.get(nome).add(new Par(transporte, Integer.parseInt(tempo.replaceAll("[^0-9]", ""))));
            });
        }

        return mapUpaESeusTransportes;
    }

    //Lista de upas e transportes para depois criar os Nos dos Grafos
    private List<NoGrafo> listUpasETranposrtes(HashMap<String, List<Par<String, Integer>>> mapUpaESeusTransportes) {
        List<NoGrafo> listUpasETransportesParaGrafo = new ArrayList<>();
        int contador = 0;
        for (Map.Entry<String, List<Par<String, Integer>>> entry : mapUpaESeusTransportes.entrySet()) {
            String upa = entry.getKey();
            List<Par<String, Integer>> transporteTempo = entry.getValue();
            listUpasETransportesParaGrafo.add(new NoGrafo(upa, Nivel.NIVEL_UPA, 0));
            if (contador == 0) {
                for (Par<String, Integer> meioDeTransporteDaVez : transporteTempo) {
                    listUpasETransportesParaGrafo.add(new NoGrafo(meioDeTransporteDaVez.getChave(), Nivel.NIVEL_MEIO_DE_TRANSPORTE, 0));
                }
            }
            contador++;
        }

        return listUpasETransportesParaGrafo;
    }

    public GrafoBuilder factory(JsonNode jsonNode){
        HashMap<String, List<Par<String, Integer>>> mapUpaESeusTransportes = mapearUpasESeusTransportes(jsonNode);
        return new GrafoBuilder(listUpasETranposrtes(mapUpaESeusTransportes),mapUpaESeusTransportes,upaService);
    }
}

