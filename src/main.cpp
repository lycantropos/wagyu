#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <mapbox/geometry/box.hpp>
#include <mapbox/geometry/point.hpp>
#include <mapbox/geometry/wagyu/edge.hpp>
#include <sstream>

namespace py = pybind11;

#define MODULE_NAME _wagyu
#define C_STR_HELPER(a) #a
#define C_STR(a) C_STR_HELPER(a)
#define BOX_NAME "Box"
#define EDGE_NAME "Edge"
#define POINT_NAME "Point"

using coordinate_t = double;
using Box = mapbox::geometry::box<coordinate_t>;
using Edge = mapbox::geometry::wagyu::edge<coordinate_t>;
using Point = mapbox::geometry::point<coordinate_t>;

static std::string bool_repr(bool value) { return py::str(py::bool_(value)); }

template <class Object>
std::string repr(const Object& object) {
  std::ostringstream stream;
  stream.precision(std::numeric_limits<double>::digits10 + 2);
  stream << object;
  return stream.str();
}

namespace mapbox {
namespace geometry {
static std::ostream& operator<<(std::ostream& stream, const Point& point) {
  return stream << C_STR(MODULE_NAME) "." POINT_NAME "(" << point.x << ", "
                << point.y << ")";
}

static std::ostream& operator<<(std::ostream& stream, const Box& box) {
  return stream << C_STR(MODULE_NAME) "." BOX_NAME "(" << box.min << ", "
                << box.max << ")";
}

namespace wagyu {
static std::ostream& operator<<(std::ostream& stream, const Edge& edge) {
  return stream << C_STR(MODULE_NAME) "." EDGE_NAME "(" << edge.bot << ", "
                << edge.top << ")";
}

static bool operator==(const Edge& left, const Edge& right) {
  return left.bot == right.bot && left.top == right.top;
}
}  // namespace wagyu
}  // namespace geometry
}  // namespace mapbox

PYBIND11_MODULE(MODULE_NAME, m) {
  m.doc() = R"pbdoc(
        Python binding of mapbox/wagyu library.
    )pbdoc";

  py::class_<Point>(m, POINT_NAME)
      .def(py::init<coordinate_t, coordinate_t>(), py::arg("x"), py::arg("y"))
      .def(py::pickle(
          [](const Point& self) {  // __getstate__
            return py::make_tuple(self.x, self.y);
          },
          [](py::tuple tuple) {  // __setstate__
            if (tuple.size() != 2) throw std::runtime_error("Invalid state!");
            return Point(tuple[0].cast<coordinate_t>(),
                         tuple[1].cast<coordinate_t>());
          }))
      .def(py::self == py::self)
      .def("__repr__", repr<Point>)
      .def_readonly("x", &Point::x)
      .def_readonly("y", &Point::y);

  py::class_<Box>(m, BOX_NAME)
      .def(py::init<Point, Point>(), py::arg("min"), py::arg("max"))
      .def(py::pickle(
          [](const Box& self) {  // __getstate__
            return py::make_tuple(self.min, self.max);
          },
          [](py::tuple tuple) {  // __setstate__
            if (tuple.size() != 2) throw std::runtime_error("Invalid state!");
            return Box(tuple[0].cast<Point>(), tuple[1].cast<Point>());
          }))
      .def(py::self == py::self)
      .def("__repr__", repr<Box>)
      .def_readonly("min", &Box::min)
      .def_readonly("max", &Box::max);

  py::class_<Edge>(m, EDGE_NAME)
      .def(py::init<Point, Point>(), py::arg("start"), py::arg("end"))
      .def(py::pickle(
          [](const Edge& self) {  // __getstate__
            return py::make_tuple(self.bot, self.top);
          },
          [](py::tuple tuple) {  // __setstate__
            if (tuple.size() != 2) throw std::runtime_error("Invalid state!");
            return Edge(tuple[0].cast<Point>(), tuple[1].cast<Point>());
          }))
      .def(py::self == py::self)
      .def("__repr__", repr<Edge>)
      .def_readonly("bottom", &Edge::bot)
      .def_readonly("top", &Edge::top)
      .def_readonly("dx", &Edge::dx);

#ifdef VERSION_INFO
  m.attr("__version__") = VERSION_INFO;
#else
  m.attr("__version__") = "dev";
#endif
}
