#include <rime_api.h>

#include <cstdlib>
#include <iostream>
#include <string>

namespace {

RimeApi* api = rime_get_api();
const char kSchema[] = "rime_frost_14key";

void require(bool condition, const std::string& message) {
  if (!condition) {
    std::cerr << "FAIL: " << message << '\n';
    std::exit(EXIT_FAILURE);
  }
}

void expect_input(RimeSessionId session, const char* raw) {
  const char* actual = api->get_input(session);
  require(actual && std::string(actual) == raw,
          std::string("expected raw input '") + raw + "', got '" + (actual ? actual : "") + "'");
}

void input(RimeSessionId session, const char* keys) {
  for (; *keys; ++keys) {
    require(api->process_key(session, *keys, 0), std::string("unhandled key: ") + *keys);
  }
}

int candidate_index(RimeSessionId session, const std::string& text, const std::string& pinyin) {
  RimeCandidateListIterator list{};
  require(api->candidate_list_begin(session, &list), "no candidates for " + text);
  int result = -1;
  while (api->candidate_list_next(&list)) {
    if (list.candidate.text && text == list.candidate.text) {
      const char* comment = list.candidate.comment;
      if (comment && pinyin == comment) {
        result = list.index;
        break;
      }
      std::cerr << "Candidate " << text << " had comment: " << (comment ? comment : "") << '\n';
    }
  }
  api->candidate_list_end(&list);
  require(result >= 0, "missing candidate " + text + " (" + pinyin + ")");
  return result;
}

}  // namespace

int main(int argc, char** argv) {
  require(argc == 3, "usage: smoke-test SHARED_DATA_DIR USER_DATA_DIR");
  RimeTraits traits{};
  RIME_STRUCT_INIT(RimeTraits, traits);
  traits.shared_data_dir = argv[1];
  traits.user_data_dir = argv[2];
  traits.app_name = "rime.rime_frost_14key_smoke_test";
  traits.min_log_level = 2;
  api->setup(&traits);
  api->initialize(&traits);
  require(api->start_maintenance(True), "could not start full deployment");
  api->join_maintenance_thread();

  RimeSchemaList schemas{};
  require(api->get_schema_list(&schemas), "could not read schema list");
  bool found = false;
  for (size_t i = 0; i < schemas.size; ++i) {
    found = found || std::string(schemas.list[i].schema_id) == kSchema;
  }
  api->free_schema_list(&schemas);
  require(found, "fourteen-key schema is missing from the schema list");

  auto session = api->create_session();
  require(session && api->select_schema(session, kSchema), "could not open fourteen-key session");
  for (char key : std::string("wryipsfhkxvn")) {
    require(!api->process_key(session, key, 0), std::string("unexpected spelling key: ") + key);
  }
  RimeCommit commit{};
  RIME_STRUCT_INIT(RimeCommit, commit);
  api->process_key(session, '\'', 0);
  require(!api->get_commit(session, &commit), "idle separator committed a quote");
  expect_input(session, "");
  for (char key : std::string("qetuoadgjlzcbm")) {
    require(api->process_key(session, key, 0), std::string("unhandled key: ") + key);
    const char raw[] = {key, '\0'};
    expect_input(session, raw);
    api->clear_composition(session);
  }

  input(session, "bu");
  expect_input(session, "bu");
  candidate_index(session, "你", "ni");
  candidate_index(session, "比", "bi");  // same raw keys, distinct candidate readings
  input(session, "gao");
  expect_input(session, "bugao");
  candidate_index(session, "你好", "ni hao");  // no separator required
  require(api->process_key(session, 0xff08, 0), "Backspace was not handled");
  expect_input(session, "buga");
  input(session, "o");
  candidate_index(session, "你好", "ni hao");
  api->clear_composition(session);

  input(session, "lue");  // lve -> lue compatibility spelling inherited from full pinyin
  candidate_index(session, "略", "lve");
  api->clear_composition(session);

  input(session, "zu'");
  expect_input(session, "zu'");
  require(!api->get_commit(session, &commit), "explicit separator committed too early");
  input(session, "ab");
  expect_input(session, "zu'ab");
  require(api->select_candidate(session, candidate_index(session, "西安", "xi an")),
          "phrase selection failed");
  require(api->get_commit(session, &commit), "selected phrase did not commit");
  require(commit.text && std::string(commit.text) == "西安", "wrong committed phrase");
  api->free_commit(&commit);
  expect_input(session, "");

  struct DoublePinyinCase {
    const char* schema;
    const char* second_syllable;
  };
  const DoublePinyinCase double_pinyin[] = {
      {"rime_frost_double_pinyin_14key", "gj"},       // ni hk -> bu gj
      {"rime_frost_double_pinyin_flypy_14key", "gc"}, // ni hc -> bu gc
  };
  for (const auto& test : double_pinyin) {
    require(api->select_schema(session, test.schema), std::string("could not select ") + test.schema);
    input(session, "bu");
    candidate_index(session, "你", "ni");
    candidate_index(session, "比", "bi");
    input(session, test.second_syllable);
    candidate_index(session, "你好", "ni hao");
    require(api->process_key(session, 0xff08, 0), "double pinyin backspace was not handled");
    expect_input(session, "bug");
    api->clear_composition(session);
    input(session, "bu'");
    require(!api->get_commit(session, &commit), "double pinyin separator committed too early");
    input(session, test.second_syllable);
    require(api->select_candidate(session, candidate_index(session, "你好", "ni hao")),
            "double pinyin phrase selection failed");
    require(api->get_commit(session, &commit), "double pinyin phrase did not commit");
    require(commit.text && std::string(commit.text) == "你好", "wrong double pinyin phrase");
    api->free_commit(&commit);
    expect_input(session, "");
  }

  api->destroy_session(session);
  api->finalize();
  std::cout << "Fourteen-key smoke test passed\n";
}
