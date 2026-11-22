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
    require(RimeProcessKey(session, *keys, 0), "stroke key was not handled");
  }
}

void expect_preedit(RimeSessionId session, const char* text) {
  RIME_STRUCT(RimeContext, context);
  require(RimeGetContext(session, &context), "cannot read Rime context");
  require(context.composition.preedit &&
              std::strcmp(context.composition.preedit, text) == 0,
          "unexpected stroke preedit");
  require(context.menu.page_size == 9, "unexpected candidate page size");
  RimeFreeContext(&context);
}

int candidate_index(RimeSessionId session, const char* text) {
  RimeCandidateListIterator list{};
  require(RimeCandidateListBegin(session, &list), "no candidates available");
  int index = -1;
  while (RimeCandidateListNext(&list)) {
    if (std::strcmp(list.candidate.text, text) == 0) {
      index = list.index;
      break;
    }
  }
  RimeCandidateListEnd(&list);
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
  RimeSetup(&traits);
  RimeInitialize(&traits);
  require(RimeStartMaintenance(True), "could not start full deployment");
  RimeJoinMaintenanceThread();

  RimeSchemaList schemas{};
  require(RimeGetSchemaList(&schemas), "could not load deployed schema list");
  bool has_stroke = false;
  for (size_t i = 0; i < schemas.size; ++i) {
    if (std::strcmp(schemas.list[i].schema_id, "rime_frost_stroke_t9") == 0) {
      has_stroke = true;
    }
  }
  RimeFreeSchemaList(&schemas);
  require(has_stroke, "stroke schema is missing from the schema list");

  auto session = RimeCreateSession();
  require(session, "could not start Rime session");
  require(RimeSelectSchema(session, "rime_frost_stroke_t9"),
          "could not load stroke schema");
  require(!RimeProcessKey(session, 'a', 0), "non-stroke letter was consumed");

  input(session, "szhs");
  expect_preedit(session, "丨乛一丨");
  candidate_index(session, "中");
  require(RimeProcessKey(session, 0xff08, 0), "Backspace was not handled");
  expect_preedit(session, "丨乛一");
  candidate_index(session, "中");  // prefix completion after deleting final stroke
  RimeClearComposition(session);

  input(session, "nhpn");
  expect_preedit(session, "丶一丿丶");
  int index = candidate_index(session, "文");
  require(rime_get_api()->select_candidate(session, index), "candidate selection failed");
  RIME_STRUCT(RimeCommit, commit);
  require(RimeGetCommit(session, &commit), "candidate did not commit");
  require(std::strcmp(commit.text, "文") == 0, "wrong character committed");
  RimeFreeCommit(&commit);

  RimeDestroySession(session);
  RimeFinalize();
  std::cout << "Stroke smoke test passed\n";
}
