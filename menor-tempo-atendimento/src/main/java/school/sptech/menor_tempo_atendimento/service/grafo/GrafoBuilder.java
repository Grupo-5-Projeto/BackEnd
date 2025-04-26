package school.sptech.menor_tempo_atendimento.service.grafo;

import school.sptech.menor_tempo_atendimento.service.upa.UpaService;
import school.sptech.menor_tempo_atendimento.domain.Nivel;
import school.sptech.menor_tempo_atendimento.domain.NoGrafo;
import school.sptech.menor_tempo_atendimento.domain.Par;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class GrafoBuilder {
    private UpaService upaService;
    private List<NoGrafo> listUpasETransportes;
    private HashMap<String, List<Par<String, Integer>>> mapUpaESeusTransportes;

    public GrafoBuilder(List<NoGrafo> listUpasETransportes, HashMap<String, List<Par<String, Integer>>> mapUpaESeusTransportes
    , UpaService upaService) {
        this.listUpasETransportes = listUpasETransportes;
        this.mapUpaESeusTransportes = mapUpaESeusTransportes;
        this.upaService = upaService;
    }

    private Map<NoGrafo, List<Par<NoGrafo, Double>>> gerarNosGrafo() {
        Map<NoGrafo, List<Par<NoGrafo, Double>>> nosGrafo = new HashMap<>();
        //Criando Nó paciente
        NoGrafo paciente = new NoGrafo("paciente", Nivel.NIVEL_PACIENTE, 0);
        nosGrafo.putIfAbsent(paciente, new ArrayList<>());
        //Criando Nós meios de transporte e upas
        for (NoGrafo meiosDeTranporteUpas : listUpasETransportes)  nosGrafo.putIfAbsent(meiosDeTranporteUpas, new ArrayList<>());
        //Criando uma lista com os nomes das upas para depois pegar o tempo de espera de cada upa
        List<String> nomesUpas = new ArrayList<>();
        for (NoGrafo meioDeTransporte : listUpasETransportes) {
            if (meioDeTransporte.getNivel() == Nivel.NIVEL_UPA) {
                nomesUpas.add(meioDeTransporte.getNome());
            }
        }
        //Criando Nós tempoDeEspera (o tempo de espera dentro da upa também é um nó)
        for (NoGrafo tempoDeEspera : upaService.getTempoEspera(nomesUpas)) nosGrafo.putIfAbsent(tempoDeEspera, new ArrayList<>());
        //Exibindo os nomes de todos os nós
        for (NoGrafo noDaVez: nosGrafo.keySet()){
            System.out.println(noDaVez.getNome());
        }
        return nosGrafo;
    }

    private Map<NoGrafo, List<Par<NoGrafo, Double>>> gerarArestasGrafo(Map<NoGrafo, List<Par<NoGrafo, Double>>> nosGrafo) {
        NoGrafo paciente = null;

        for (NoGrafo no : nosGrafo.keySet()) {
            if ("paciente".equals(no.getNome())) {
                paciente = no;
                break;
            }
        }
        //Criando as conexões das arestas do grafo
        //Como é um hashMap essas conexões ficam da seguinte maneira: chave (nó) / valor (lista de nós que tem conexão)
        for (NoGrafo no : nosGrafo.keySet()) {
            //Primeiro nivel de conexão é entre o paciente e os meios de transporte
            if (no.getNivel() == Nivel.NIVEL_MEIO_DE_TRANSPORTE) {
                nosGrafo.get(paciente).add(new Par<>(no, (double) no.getTempo()));
                nosGrafo.get(no).add(new Par<>(paciente, (double) no.getTempo()));
            }
            //Segundo nivel de conexão é entre upa e meios de transporte
            if (no.getNivel() == Nivel.NIVEL_UPA) {
                for (NoGrafo noDaVez : nosGrafo.keySet()) {
                    if (noDaVez.getNivel() == Nivel.NIVEL_MEIO_DE_TRANSPORTE) {
                        //Procurando por todos os meios de transporte, preciso do mapUpaESeusTransportes para pegar o valores dos meios de transporte
                        for (Par<String, Integer> tempoMeioDeTransporteUpa : mapUpaESeusTransportes.get(no.getNome())) {
                            if (tempoMeioDeTransporteUpa.getChave().equals(noDaVez.getNome())) {
                                nosGrafo.get(no).add(new Par<>(noDaVez, (double) tempoMeioDeTransporteUpa.getValor()));
                                nosGrafo.get(noDaVez).add(new Par<>(no, (double) tempoMeioDeTransporteUpa.getValor()));
                            }
                        }
                    }
                }
            }
            //Terceiro nivel de conexão é entre tempoDeEspera e upa
            if (no.getNivel() == Nivel.NIVEL_TEMPO_DE_ESPERA) {
                for (NoGrafo noDaVez : nosGrafo.keySet()) {
                    if (noDaVez.getNivel() == Nivel.NIVEL_UPA) {
                        if (no.getNome().equals(noDaVez.getNome() + "-" + "tempoEspera")) {
                            nosGrafo.get(no).add(new Par<>(noDaVez, (double) no.getTempo()));
                            nosGrafo.get(noDaVez).add(new Par<>(no, (double) no.getTempo()));
                        }
                    }
                }
            }
        }
        return nosGrafo;
    }

    public Map<NoGrafo, List<Par<NoGrafo, Double>>> build(){
        return gerarArestasGrafo(gerarNosGrafo());
    }
}
