#include <rime_api.h>

#include <cstdlib>
#include <cstring>
#include <iostream>

namespace {

void require(bool condition, const char* message) {
  if (!condition) {
    std::cerr << "FAIL: " << message << '\n';
    std::exit(EXIT_FAILURE);
  }
}

void input(RimeSessionId session, const char* keys) {
  for (; *keys; ++keys) {
    require(rime_get_api()->process_key(session, *keys, 0), "stroke key was not handled");
  }
}

void expect_preedit(RimeSessionId session, const char* text) {
  RIME_STRUCT(RimeContext, context);
  require(rime_get_api()->get_context(session, &context), "cannot read Rime context");
  require(context.composition.preedit &&
              std::strcmp(context.composition.preedit, text) == 0,
          "unexpected stroke preedit");
  require(context.menu.page_size == 9, "unexpected candidate page size");
  rime_get_api()->free_context(&context);
}

int candidate_index(RimeSessionId session, const char* text) {
  RimeCandidateListIterator list{};
  require(rime_get_api()->candidate_list_begin(session, &list), "no candidates available");
  int index = -1;
  while (rime_get_api()->candidate_list_next(&list)) {
    if (std::strcmp(list.candidate.text, text) == 0) {
      index = list.index;
      break;
    }
  }
  rime_get_api()->candidate_list_end(&list);
  if (index < 0) std::cerr << "Missing candidate: " << text << '\n';
  require(index >= 0, "expected character not found in candidate list");
  return index;
}

}  // namespace

int main(int argc, char** argv) {
  require(argc == 3, "usage: smoke-test SHARED_DATA_DIR USER_DATA_DIR");
  RIME_STRUCT(RimeTraits, traits);
  traits.shared_data_dir = argv[1];
  traits.user_data_dir = argv[2];
  traits.app_name = "rime.rime_frost_stroke_t9_smoke_test";
  traits.min_log_level = 2;
  rime_get_api()->setup(&traits);
  rime_get_api()->initialize(&traits);
  require(rime_get_api()->start_maintenance(True), "could not start full deployment");
  rime_get_api()->join_maintenance_thread();

  RimeSchemaList schemas{};
  require(rime_get_api()->get_schema_list(&schemas), "could not load deployed schema list");
  bool has_stroke = false;
  for (size_t i = 0; i < schemas.size; ++i) {
    if (std::strcmp(schemas.list[i].schema_id, "rime_frost_stroke_t9") == 0) {
      has_stroke = true;
    }
  }
  rime_get_api()->free_schema_list(&schemas);
  require(has_stroke, "stroke schema is missing from the schema list");

  auto session = rime_get_api()->create_session();
  require(session, "could not start Rime session");
  require(rime_get_api()->select_schema(session, "rime_frost_stroke_t9"),
          "could not load stroke schema");
  require(!rime_get_api()->process_key(session, 'a', 0), "non-stroke letter was consumed");

  input(session, "szhs");
  expect_preedit(session, "丨乛一丨");
  candidate_index(session, "中");
  require(rime_get_api()->process_key(session, 0xff08, 0), "Backspace was not handled");
  expect_preedit(session, "丨乛一");
  candidate_index(session, "中");  // prefix completion after deleting final stroke
  rime_get_api()->clear_composition(session);

  input(session, "nhpn");
  expect_preedit(session, "丶一丿丶");
  int index = candidate_index(session, "文");
  require(rime_get_api()->select_candidate(session, index), "candidate selection failed");
  RIME_STRUCT(RimeCommit, commit);
  require(rime_get_api()->get_commit(session, &commit), "candidate did not commit");
  require(std::strcmp(commit.text, "文") == 0, "wrong character committed");
  rime_get_api()->free_commit(&commit);

  input(session, "'");  // No separator text at idle.
  require(!rime_get_api()->get_commit(session, &commit), "idle separator committed text");
  input(session, "sxhs");
  expect_preedit(session, "丨＊一丨");
  require(candidate_index(session, "中") == 0, "中 is not the first wildcard candidate");
  input(session, "'");
  require(!rime_get_api()->get_commit(session, &commit), "separator committed too early");
  input(session, "nhpn");
  index = candidate_index(session, "文");
  require(rime_get_api()->select_candidate(session, index), "second segment selection failed");
  require(rime_get_api()->get_commit(session, &commit), "combined candidates did not commit");
  require(std::strcmp(commit.text, "中文") == 0, "wrong text after separator");
  rime_get_api()->free_commit(&commit);

  rime_get_api()->destroy_session(session);
  rime_get_api()->finalize();
  std::cout << "Stroke smoke test passed\n";
}
